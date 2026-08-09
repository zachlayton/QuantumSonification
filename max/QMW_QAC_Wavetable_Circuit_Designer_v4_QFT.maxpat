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
		"rect" : [ 203.0, 100.0, 1275.0, 816.0 ],
		"openinpresentation" : 1,
		"gridsize" : [ 15.0, 15.0 ],
		"boxes" : [ 			{
				"box" : 				{
					"id" : "obj-5",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 160.0, 944.0, 79.0, 22.0 ],
					"text" : "phasor~ 0.15"
				}

			}
, 			{
				"box" : 				{
					"fontsize" : 18.0,
					"id" : "title",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 28.0, 22.0, 850.0, 27.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 28.0, 22.0, 850.0, 27.0 ],
					"text" : "QAC QFT CIRCUIT DESIGNER V3 → COMPACT STATE → DUAL RENDERERS",
					"textcolor" : [ 0.85, 0.93, 1.0, 1.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "instructions",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 28.0, 56.0, 880.0, 20.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 28.0, 56.0, 880.0, 20.0 ],
					"text" : "Design locally and press SEND QASM. Python bridge mode determines local-only or one confirmed IBM hardware job.",
					"textcolor" : [ 0.65, 0.72, 0.82, 1.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "qac",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 28.0, 835.0, 235.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 28.0, 78.0, 235.0, 22.0 ],
					"text" : "och.microqiskit qc 4 4 sim 256 1"
				}

			}
, 			{
				"box" : 				{
					"id" : "sender",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 285.0, 835.0, 180.0, 22.0 ],
					"text" : "qac_wavetable_sender_v1"
				}

			}
, 			{
				"box" : 				{
					"id" : "sendstatus",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 485.0, 835.0, 360.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 495.0, 885.0, 440.0, 22.0 ],
					"text" : "sender ready"
				}

			}
, 			{
				"box" : 				{
					"id" : "udp",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 28.0, 540.0, 132.0, 22.0 ],
					"text" : "udpreceive 7412"
				}

			}
, 			{
				"box" : 				{
					"id" : "oroute",
					"linecount" : 2,
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 9,
					"outlettype" : [ "", "", "", "", "", "", "", "", "FullPacket" ],
					"patching_rect" : [ 175.0, 540.0, 610.0, 35.0 ],
					"text" : "o.route /qmw/wavetable/points /qmw/wavetable/status /qmw/wavetable/error /qmw/wavetable/correlations /qmw/wavetable/pauli15 /qmw/wavetable/surface_file /qmw/quantum/features /qmw/quantum/state"
				}

			}
, 			{
				"box" : 				{
					"id" : "rawprint",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 625.0, 580.0, 135.0, 22.0 ],
					"text" : "print WTABLE_RAW"
				}

			}
, 			{
				"box" : 				{
					"id" : "loader",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 3,
					"outlettype" : [ "", "", "" ],
					"patching_rect" : [ 28.0, 590.0, 195.0, 22.0 ],
					"saved_object_attributes" : 					{
						"filename" : "qmw_wavetable_receiver_v4.js",
						"parameter_enable" : 0
					}
,
					"text" : "js qmw_wavetable_receiver_v4.js"
				}

			}
, 			{
				"box" : 				{
					"id" : "buffer",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "float", "bang" ],
					"patching_rect" : [ 28.0, 635.0, 290.0, 22.0 ],
					"text" : "buffer~ qmw_wavetable @samps 1024 @channels 1"
				}

			}
, 			{
				"box" : 				{
					"bgcolor" : [ 0.08, 0.1, 0.14, 1.0 ],
					"id" : "display",
					"maxclass" : "multislider",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 28.0, 740.0, 880.0, 100.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 28.0, 740.0, 880.0, 100.0 ],
					"size" : 256,
					"slidercolor" : [ 0.34, 0.78, 1.0, 1.0 ]
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "freq",
					"maxclass" : "flonum",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 28.0, 855.0, 75.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 33.0, 854.0, 75.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "freqlabel",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 110.0, 855.0, 95.0, 20.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 110.0, 855.0, 95.0, 20.0 ],
					"text" : "frequency Hz",
					"textcolor" : [ 0.7, 0.76, 0.84, 1.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "phasor",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 28.0, 895.0, 78.0, 22.0 ],
					"text" : "phasor~ 110."
				}

			}
, 			{
				"box" : 				{
					"id" : "gain",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 458.0, 960.0, 52.0, 22.0 ],
					"text" : "*~ 1."
				}

			}
, 			{
				"box" : 				{
					"id" : "dac",
					"maxclass" : "ezdac~",
					"numinlets" : 2,
					"numoutlets" : 0,
					"patching_rect" : [ 240.0, 944.0, 45.0, 45.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 345.0, 885.0, 45.0, 45.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "statuslabel",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 430.0, 855.0, 62.0, 20.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 425.0, 840.0, 62.0, 20.0 ],
					"text" : "STATUS",
					"textcolor" : [ 0.34, 0.78, 1.0, 1.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "status",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 500.0, 852.0, 408.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 500.0, 852.0, 408.0, 22.0 ],
					"text" : "waiting for wavetable"
				}

			}
, 			{
				"box" : 				{
					"id" : "print",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 780.0, 540.0, 150.0, 22.0 ],
					"text" : "print WTABLE_OTHER"
				}

			}
, 			{
				"box" : 				{
					"id" : "corr_unpack",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 4,
					"outlettype" : [ "int", "float", "float", "float" ],
					"patching_rect" : [ 505.0, 580.0, 90.0, 22.0 ],
					"text" : "unpack i f f f"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "xx",
					"maxclass" : "flonum",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 610.0, 580.0, 65.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 610.0, 635.0, 65.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "yy",
					"maxclass" : "flonum",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 690.0, 580.0, 65.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 690.0, 635.0, 65.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "zz",
					"maxclass" : "flonum",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 770.0, 580.0, 65.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 770.0, 635.0, 65.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "corr_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 610.0, 608.0, 230.0, 20.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 610.0, 662.0, 230.0, 20.0 ],
					"text" : "XX                 YY                 ZZ",
					"textcolor" : [ 0.51, 0.81, 1.0, 1.0 ]
				}

			}
, 			{
				"box" : 				{
					"filename" : "qmw_qac_wavetable_designer_v1.js",
					"id" : "designer",
					"jsarguments" : [ "qmw_qac_wavetable_designer_v1.js" ],
					"maxclass" : "jsui",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 28.0, 100.0, 780.0, 390.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 28.0, 100.0, 780.0, 390.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "designer_status_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 820.0, 110.0, 120.0, 20.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 820.0, 110.0, 120.0, 20.0 ],
					"text" : "DESIGNER STATUS",
					"textcolor" : [ 0.34, 0.78, 1.0, 1.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "designer_status",
					"linecount" : 2,
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 820.0, 138.0, 140.0, 35.0 ],
					"presentation" : 1,
					"presentation_linecount" : 2,
					"presentation_rect" : [ 820.0, 138.0, 140.0, 35.0 ],
					"text" : "\"sent 2 gates → QASM bridge\""
				}

			}
, 			{
				"box" : 				{
					"id" : "safety",
					"linecount" : 8,
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 820.0, 230.0, 143.0, 114.0 ],
					"presentation" : 1,
					"presentation_linecount" : 8,
					"presentation_rect" : [ 820.0, 230.0, 143.0, 114.0 ],
					"text" : "LOCAL MODE:\nSEND freely.\n\nBOTH MODE:\nEvery SEND QASM creates an IBM job. Submit deliberately, then stop the bridge.",
					"textcolor" : [ 1.0, 0.68, 0.3, 1.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "pauli_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 28.0, 505.0, 880.0, 20.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 28.0, 505.0, 880.0, 20.0 ],
					"text" : "PAULI-15 EXPECTATIONS   XI YI ZI | IX IY IZ | XX XY XZ YX YY YZ ZX ZY ZZ",
					"textcolor" : [ 0.51, 0.81, 1.0, 1.0 ]
				}

			}
, 			{
				"box" : 				{
					"bgcolor" : [ 0.08, 0.1, 0.14, 1.0 ],
					"id" : "pauli_display",
					"maxclass" : "multislider",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 28.0, 530.0, 880.0, 90.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 28.0, 530.0, 880.0, 90.0 ],
					"setstyle" : 1,
					"size" : 15,
					"slidercolor" : [ 0.95, 0.55, 0.25, 1.0 ],
					"spacing" : 10
				}

			}
, 			{
				"box" : 				{
					"id" : "pauli_slice",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 2,
					"outlettype" : [ "", "" ],
					"patching_rect" : [ 600.0, 895.0, 62.0, 22.0 ],
					"text" : "zl.slice 1"
				}

			}
, 			{
				"box" : 				{
					"id" : "surface_loader",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "" ],
					"patching_rect" : [ 600.0, 865.0, 220.0, 22.0 ],
					"saved_object_attributes" : 					{
						"filename" : "qmw_pauli_surface_receiver_v1.js",
						"parameter_enable" : 0
					}
,
					"text" : "js qmw_pauli_surface_receiver_v1.js"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "morph",
					"maxclass" : "flonum",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 76.0, 944.0, 75.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 220.0, 855.0, 75.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "morph_label",
					"linecount" : 3,
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 441.0, 895.0, 190.0, 47.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 495.0, 828.0, 390.0, 20.0 ],
					"text" : "spectral view: 0=direct  .33=shifted  .67=stretched  1=reversed",
					"textcolor" : [ 0.51, 0.81, 1.0, 1.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "morph_line",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 2,
					"outlettype" : [ "signal", "bang" ],
					"patching_rect" : [ 300.0, 885.0, 42.0, 22.0 ],
					"text" : "line~"
				}

			}
, 			{
				"box" : 				{
					"id" : "two_d",
					"maxclass" : "newobj",
					"numinlets" : 4,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 185.0, 895.0, 185.0, 22.0 ],
					"text" : "2d.wave~ qmw_wavetable"
				}

			}
, 			{
				"box" : 				{
					"id" : "rows",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 550.0, 948.5, 44.0, 22.0 ],
					"text" : "rows 4"
				}

			}
, 			{
				"box" : 				{
					"id" : "rows_load",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "bang" ],
					"patching_rect" : [ 550.0, 885.0, 60.0, 22.0 ],
					"text" : "loadbang"
				}

			}
, 			{
				"box" : 				{
					"id" : "surface_replace",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 830.0, 865.0, 105.0, 22.0 ],
					"text" : "prepend replace"
				}

			}
, 			{
				"box" : 				{
					"id" : "surface_slice",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 2,
					"outlettype" : [ "", "" ],
					"patching_rect" : [ 830.0, 835.0, 62.0, 22.0 ],
					"text" : "zl.slice 1"
				}

			}
, 			{
				"box" : 				{
					"id" : "controls_slice",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 2,
					"outlettype" : [ "", "" ],
					"patching_rect" : [ 690.0, 930.0, 62.0, 22.0 ],
					"text" : "zl.slice 1"
				}

			}
, 			{
				"box" : 				{
					"id" : "controls_unpack",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 4,
					"outlettype" : [ "float", "float", "float", "float" ],
					"patching_rect" : [ 760.0, 930.0, 105.0, 22.0 ],
					"text" : "unpack f f f f"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "entanglement_display",
					"maxclass" : "flonum",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 125.0, 945.0, 72.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 125.0, 945.0, 72.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "theta_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 680.0, 800.0, 287.0, 20.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 864.0, 355.0, 287.0, 20.0 ],
					"text" : "PARAMETERIZED: choose RX / RY / RZ, then theta"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "theta_control",
					"maxclass" : "flonum",
					"maximum" : 1.0,
					"minimum" : 0.0,
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 680.0, 825.0, 70.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 820.0, 451.0, 70.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "theta_send",
					"maxclass" : "button",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 760.0, 825.0, 24.0, 24.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 900.0, 451.0, 24.0, 24.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "theta_send_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 790.0, 827.0, 158.0, 20.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 966.0, 470.0, 158.0, 20.0 ],
					"text" : "SEND 2-QUBIT TEMPLATE"
				}

			}
, 			{
				"box" : 				{
					"id" : "theta_qasm",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "" ],
					"patching_rect" : [ 680.0, 970.0, 205.0, 22.0 ],
					"saved_object_attributes" : 					{
						"filename" : "qmw_parameterized_bell_v1.js",
						"parameter_enable" : 0
					}
,
					"text" : "js qmw_parameterized_bell_v1.js"
				}

			}
, 			{
				"box" : 				{
					"id" : "axis_rx",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 680.0, 855.0, 35.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 820.0, 480.0, 35.0, 22.0 ],
					"text" : "rx"
				}

			}
, 			{
				"box" : 				{
					"id" : "axis_ry",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 720.0, 855.0, 35.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 860.0, 480.0, 35.0, 22.0 ],
					"text" : "ry"
				}

			}
, 			{
				"box" : 				{
					"id" : "axis_rz",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 760.0, 855.0, 35.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 900.0, 480.0, 35.0, 22.0 ],
					"text" : "rz"
				}

			}
, 			{
				"box" : 				{
					"id" : "axis_note",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 805.0, 855.0, 184.0, 20.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 820.0, 507.0, 184.0, 20.0 ],
					"text" : "Main SEND applies local rotation"
				}

			}
, 			{
				"box" : 				{
					"id" : "feature_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 28.0, 920.0, 450.0, 20.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 28.0, 920.0, 450.0, 20.0 ],
					"text" : "RAW QUANTUM FEATURES (dimensionless)"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "polarization_display",
					"maxclass" : "flonum",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 23.0, 944.0, 72.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 28.0, 942.0, 72.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "polarization_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 28.0, 970.0, 90.0, 20.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 28.0, 970.0, 90.0, 20.0 ],
					"text" : "polarization"
				}

			}
, 			{
				"box" : 				{
					"id" : "entanglement_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 125.0, 970.0, 90.0, 20.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 125.0, 970.0, 90.0, 20.0 ],
					"text" : "entanglement"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "correlation_display",
					"maxclass" : "flonum",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 225.0, 945.0, 72.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 225.0, 945.0, 72.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "correlation_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 225.0, 970.0, 100.0, 20.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 225.0, 970.0, 100.0, 20.0 ],
					"text" : "correlation RMS"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "entropy_display",
					"maxclass" : "flonum",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 335.0, 945.0, 72.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 335.0, 945.0, 72.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "entropy_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 335.0, 970.0, 100.0, 20.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 335.0, 970.0, 100.0, 20.0 ],
					"text" : "Z entropy"
				}

			}
, 			{
				"box" : 				{
					"id" : "mapping_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 470.0, 920.0, 480.0, 20.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 470.0, 920.0, 480.0, 20.0 ],
					"text" : "EXPLICIT SONIFICATION CHOICES: pitch min/max Hz | scan min/max Hz"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "pitch_min",
					"maxclass" : "flonum",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 470.0, 945.0, 72.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 470.0, 945.0, 72.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "pitch_max",
					"maxclass" : "flonum",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 550.0, 945.0, 72.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 550.0, 945.0, 72.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "scan_min",
					"maxclass" : "flonum",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 670.0, 945.0, 72.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 670.0, 945.0, 72.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "scan_max",
					"maxclass" : "flonum",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 750.0, 945.0, 72.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 750.0, 945.0, 72.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "pitch_map",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 470.0, 995.0, 280.0, 22.0 ],
					"text" : "expr 55. * pow(8.\\, (($f1 + 1.) * 0.5))"
				}

			}
, 			{
				"box" : 				{
					"id" : "scan_map",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 760.0, 995.0, 220.0, 22.0 ],
					"text" : "expr 0.05 + 0.95 * $f1"
				}

			}
, 			{
				"box" : 				{
					"id" : "entropy_sig",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 335.0, 1025.0, 44.0, 22.0 ],
					"text" : "sig~ 1."
				}

			}
, 			{
				"box" : 				{
					"id" : "y_depth_mul",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 380.0, 1025.0, 42.0, 22.0 ],
					"text" : "*~"
				}

			}
, 			{
				"box" : 				{
					"id" : "gain_map",
					"maxclass" : "newobj",
					"numinlets" : 3,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 470.0, 1055.0, 220.0, 22.0 ],
					"text" : "expr $f1 * ($f3 - $f2) + $f2"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "gain_min",
					"maxclass" : "flonum",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 850.0, 945.0, 60.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 850.0, 945.0, 60.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "gain_max",
					"maxclass" : "flonum",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 915.0, 945.0, 60.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 915.0, 945.0, 60.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "gain_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 850.0, 970.0, 139.0, 20.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 850.0, 970.0, 139.0, 20.0 ],
					"text" : "correlation gain min/max"
				}

			}
, 			{
				"box" : 				{
					"id" : "gain_min_default",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 700.0, 1055.0, 90.0, 22.0 ],
					"text" : "loadmess 0.03"
				}

			}
, 			{
				"box" : 				{
					"id" : "gain_max_default",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 800.0, 1055.0, 85.0, 22.0 ],
					"text" : "loadmess 0.2"
				}

			}
, 			{
				"box" : 				{
					"id" : "rotation_layer",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "" ],
					"patching_rect" : [ 680.0, 1090.0, 225.0, 22.0 ],
					"saved_object_attributes" : 					{
						"filename" : "qmw_qasm_rotation_layer_v2.js",
						"parameter_enable" : 0
					}
,
					"text" : "js qmw_qasm_rotation_layer_v2.js"
				}

			}
, 			{
				"box" : 				{
					"id" : "rotation_target",
					"maxclass" : "number",
					"maximum" : 3,
					"minimum" : 0,
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 820.0, 535.0, 50.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 820.0, 535.0, 50.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "rotation_target_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 875.0, 535.0, 75.0, 20.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 875.0, 535.0, 75.0, 20.0 ],
					"text" : "target qubit"
				}

			}
, 			{
				"box" : 				{
					"id" : "rotation_enable",
					"maxclass" : "toggle",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "int" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 820.0, 565.0, 24.0, 24.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 820.0, 565.0, 24.0, 24.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "rotation_enable_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 850.0, 567.0, 150.0, 20.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 850.0, 567.0, 150.0, 20.0 ],
					"text" : "apply to designer circuit"
				}

			}
, 			{
				"box" : 				{
					"id" : "rotation_target_prepend",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 910.0, 1090.0, 95.0, 22.0 ],
					"text" : "prepend target"
				}

			}
, 			{
				"box" : 				{
					"id" : "rotation_enable_prepend",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 910.0, 1120.0, 95.0, 22.0 ],
					"text" : "prepend enable"
				}

			}
, 			{
				"box" : 				{
					"id" : "rotation_theta_prepend",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 910.0, 1150.0, 95.0, 22.0 ],
					"text" : "prepend theta"
				}

			}
, 			{
				"box" : 				{
					"id" : "rotation_enable_default",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 820.0, 1120.0, 80.0, 22.0 ],
					"text" : "loadmess 1"
				}

			}
, 			{
				"box" : 				{
					"id" : "v3_renderer",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 7,
					"outlettype" : [ "", "", "", "", "", "", "" ],
					"patching_rect" : [ 20.0, 1090.0, 255.0, 22.0 ],
					"saved_object_attributes" : 					{
						"filename" : "qmw_compact_state_renderer_v4.js",
						"parameter_enable" : 0
					}
,
					"text" : "js qmw_compact_state_renderer_v4.js"
				}

			}
, 			{
				"box" : 				{
					"id" : "v3_local_buffer",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "float", "bang" ],
					"patching_rect" : [ 20.0, 1120.0, 280.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 30.0, 644.0, 280.0, 22.0 ],
					"text" : "buffer~ qmw_v4_local @samps 1024 @channels 1"
				}

			}
, 			{
				"box" : 				{
					"id" : "v3_ibm_buffer",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "float", "bang" ],
					"patching_rect" : [ 300.0, 1120.0, 274.0, 22.0 ],
					"text" : "buffer~ qmw_v4_ibm @samps 1024 @channels 1"
				}

			}
, 			{
				"box" : 				{
					"id" : "v3_local_wave",
					"maxclass" : "newobj",
					"numinlets" : 4,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 20.0, 1150.0, 160.0, 22.0 ],
					"text" : "2d.wave~ qmw_v4_local"
				}

			}
, 			{
				"box" : 				{
					"id" : "v3_ibm_wave",
					"maxclass" : "newobj",
					"numinlets" : 4,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 190.0, 1150.0, 155.0, 22.0 ],
					"text" : "2d.wave~ qmw_v4_ibm"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "source_xfade",
					"maxclass" : "flonum",
					"maximum" : 1.0,
					"minimum" : 0.0,
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 30.0, 1005.0, 75.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 30.0, 1005.0, 75.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "source_xfade_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 110.0, 1007.0, 210.0, 20.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 110.0, 1007.0, 210.0, 20.0 ],
					"text" : "source: 0=LOCAL   1=IBM"
				}

			}
, 			{
				"box" : 				{
					"id" : "source_xfade_pack",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 360.0, 1150.0, 75.0, 22.0 ],
					"text" : "pack 0. 50"
				}

			}
, 			{
				"box" : 				{
					"id" : "source_xfade_line",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 2,
					"outlettype" : [ "signal", "bang" ],
					"patching_rect" : [ 440.0, 1150.0, 42.0, 22.0 ],
					"text" : "line~"
				}

			}
, 			{
				"box" : 				{
					"id" : "source_xfade_inverse",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 490.0, 1150.0, 52.0, 22.0 ],
					"text" : "!-~ 1."
				}

			}
, 			{
				"box" : 				{
					"id" : "source_local_mul",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 550.0, 1150.0, 42.0, 22.0 ],
					"text" : "*~"
				}

			}
, 			{
				"box" : 				{
					"id" : "source_ibm_mul",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 600.0, 1150.0, 42.0, 22.0 ],
					"text" : "*~"
				}

			}
, 			{
				"box" : 				{
					"id" : "source_sum",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 650.0, 1150.0, 42.0, 22.0 ],
					"text" : "+~"
				}

			}
, 			{
				"box" : 				{
					"id" : "render_mode_ifft",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 340.0, 1005.0, 70.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 340.0, 996.0, 70.0, 22.0 ],
					"text" : "mode ifft"
				}

			}
, 			{
				"box" : 				{
					"id" : "render_mode_spline",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 415.0, 1005.0, 85.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 415.0, 996.0, 85.0, 22.0 ],
					"text" : "mode spline"
				}

			}
, 			{
				"box" : 				{
					"id" : "render_mode_density",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 505.0, 1005.0, 90.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 505.0, 996.0, 90.0, 22.0 ],
					"text" : "mode density"
				}

			}
, 			{
				"box" : 				{
					"id" : "render_mode_hybrid",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 600.0, 1005.0, 85.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 600.0, 996.0, 85.0, 22.0 ],
					"text" : "mode hybrid"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "render_spectral",
					"maxclass" : "flonum",
					"maximum" : 1.0,
					"minimum" : 0.0,
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 340.0, 1040.0, 65.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 340.0, 1028.0, 65.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "render_spectral_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 410.0, 1042.0, 125.0, 20.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 410.0, 1030.0, 125.0, 20.0 ],
					"text" : "spectral -> spatial"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "render_detail",
					"maxclass" : "flonum",
					"maximum" : 1.0,
					"minimum" : 0.0,
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 540.0, 1040.0, 65.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 540.0, 1028.0, 65.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "render_detail_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 610.0, 1042.0, 120.0, 20.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 610.0, 1030.0, 120.0, 20.0 ],
					"text" : "smooth -> detailed"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "render_nonlinear",
					"maxclass" : "flonum",
					"maximum" : 1.0,
					"minimum" : 0.0,
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 735.0, 1040.0, 65.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 735.0, 1028.0, 65.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "render_nonlinear_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 805.0, 1042.0, 150.0, 20.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 805.0, 1030.0, 150.0, 20.0 ],
					"text" : "stable -> nonlinear"
				}

			}
, 			{
				"box" : 				{
					"id" : "render_spectral_prepend",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 700.0, 1090.0, 105.0, 22.0 ],
					"text" : "prepend spectral"
				}

			}
, 			{
				"box" : 				{
					"id" : "render_detail_prepend",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 810.0, 1090.0, 95.0, 22.0 ],
					"text" : "prepend detail"
				}

			}
, 			{
				"box" : 				{
					"id" : "render_nonlinear_prepend",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 910.0, 1090.0, 115.0, 22.0 ],
					"text" : "prepend nonlinear"
				}

			}
, 			{
				"box" : 				{
					"id" : "v3_local_xyz_unpack",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 3,
					"outlettype" : [ "float", "float", "float" ],
					"patching_rect" : [ 280.0, 1090.0, 105.0, 22.0 ],
					"text" : "unpack f f f"
				}

			}
, 			{
				"box" : 				{
					"id" : "v3_ibm_xyz_unpack",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 3,
					"outlettype" : [ "float", "float", "float" ],
					"patching_rect" : [ 390.0, 1090.0, 105.0, 22.0 ],
					"text" : "unpack f f f"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "ibm_xx",
					"maxclass" : "flonum",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 610.0, 690.0, 65.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 610.0, 690.0, 65.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "ibm_yy",
					"maxclass" : "flonum",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 690.0, 690.0, 65.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 690.0, 690.0, 65.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "ibm_zz",
					"maxclass" : "flonum",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 770.0, 690.0, 65.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 770.0, 690.0, 65.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "v3_xyz_labels",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 610.0, 715.0, 295.0, 20.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 610.0, 715.0, 295.0, 20.0 ],
					"text" : "LOCAL XX / YY / ZZ above     IBM XX / YY / ZZ below"
				}

			}
, 			{
				"box" : 				{
					"id" : "ir_local_buffer",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "float", "bang" ],
					"patching_rect" : [ 20.0, 1180.0, 306.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 33.0, 672.0, 306.0, 22.0 ],
					"text" : "buffer~ qmw_v4_ir_local @samps 262144 @channels 1"
				}

			}
, 			{
				"box" : 				{
					"id" : "ir_ibm_buffer",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "float", "bang" ],
					"patching_rect" : [ 330.0, 1180.0, 301.0, 22.0 ],
					"text" : "buffer~ qmw_v4_ir_ibm @samps 262144 @channels 1"
				}

			}
, 			{
				"box" : 				{
					"id" : "ir_convolver",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "signal", "signal" ],
					"patching_rect" : [ 20.0, 1210.0, 190.0, 22.0 ],
					"text" : "multiconvolve~ 1 2 medium"
				}

			}
, 			{
				"box" : 				{
					"id" : "ir_set_local",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 220.0, 1210.0, 180.0, 22.0 ],
					"text" : "set 1 1 qmw_v4_ir_local 1"
				}

			}
, 			{
				"box" : 				{
					"id" : "ir_set_ibm",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 410.0, 1210.0, 175.0, 22.0 ],
					"text" : "set 1 2 qmw_v4_ir_ibm 1"
				}

			}
, 			{
				"box" : 				{
					"id" : "ir_local_mul",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 20.0, 1240.0, 42.0, 22.0 ],
					"text" : "*~"
				}

			}
, 			{
				"box" : 				{
					"id" : "ir_ibm_mul",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 70.0, 1240.0, 42.0, 22.0 ],
					"text" : "*~"
				}

			}
, 			{
				"box" : 				{
					"id" : "ir_wet_sum",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 120.0, 1240.0, 42.0, 22.0 ],
					"text" : "+~"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "ir_drywet",
					"maxclass" : "flonum",
					"maximum" : 1.0,
					"minimum" : 0.0,
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 30.0, 1080.0, 75.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 30.0, 1038.0, 75.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "ir_drywet_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 110.0, 1082.0, 180.0, 20.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 110.0, 1040.0, 180.0, 20.0 ],
					"text" : "quantum IR: 0=dry  1=wet"
				}

			}
, 			{
				"box" : 				{
					"id" : "ir_drywet_pack",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 180.0, 1240.0, 75.0, 22.0 ],
					"text" : "pack 0. 50"
				}

			}
, 			{
				"box" : 				{
					"id" : "ir_drywet_line",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 2,
					"outlettype" : [ "signal", "bang" ],
					"patching_rect" : [ 265.0, 1240.0, 42.0, 22.0 ],
					"text" : "line~"
				}

			}
, 			{
				"box" : 				{
					"id" : "ir_dry_inverse",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 315.0, 1240.0, 52.0, 22.0 ],
					"text" : "!-~ 1."
				}

			}
, 			{
				"box" : 				{
					"id" : "ir_dry_mul",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 375.0, 1240.0, 42.0, 22.0 ],
					"text" : "*~"
				}

			}
, 			{
				"box" : 				{
					"id" : "ir_wet_mul",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 425.0, 1240.0, 42.0, 22.0 ],
					"text" : "*~"
				}

			}
, 			{
				"box" : 				{
					"id" : "ir_mix_sum",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 475.0, 1240.0, 42.0, 22.0 ],
					"text" : "+~"
				}

			}
, 			{
				"box" : 				{
					"id" : "ir_dry_sqrt",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 525.0, 1240.0, 42.0, 22.0 ],
					"text" : "sqrt~"
				}

			}
, 			{
				"box" : 				{
					"id" : "ir_wet_sqrt",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 575.0, 1240.0, 42.0, 22.0 ],
					"text" : "sqrt~"
				}

			}
, 			{
				"box" : 				{
					"id" : "local_monitor_gain",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 20.0, 1185.0, 62.0, 22.0 ],
					"text" : "*~ 0.12"
				}

			}
, 			{
				"box" : 				{
					"id" : "qft_selector_label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 900.0, 455.0, 190.0, 20.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 944.0, 384.0, 190.0, 20.0 ],
					"text" : "POST-CIRCUIT TRANSFORM"
				}

			}
, 			{
				"box" : 				{
					"id" : "qft_none",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 900.0, 480.0, 55.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 900.0, 480.0, 55.0, 22.0 ],
					"text" : "none"
				}

			}
, 			{
				"box" : 				{
					"id" : "qft_qft",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 960.0, 480.0, 55.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 1004.0, 409.0, 55.0, 22.0 ],
					"text" : "qft"
				}

			}
, 			{
				"box" : 				{
					"id" : "qft_iqft",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1020.0, 480.0, 55.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 1064.0, 409.0, 55.0, 22.0 ],
					"text" : "iqft"
				}

			}
, 			{
				"box" : 				{
					"id" : "qft_pack",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "FullPacket" ],
					"patching_rect" : [ 900.0, 515.0, 220.0, 22.0 ],
					"text" : "o.pack /qmw/wavetable/transform"
				}

			}
, 			{
				"box" : 				{
					"id" : "qft_udp",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 900.0, 550.0, 165.0, 22.0 ],
					"text" : "udpsend 127.0.0.1 7411"
				}

			}
, 			{
				"box" : 				{
					"id" : "qft_default",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1080.0, 480.0, 85.0, 22.0 ],
					"text" : "loadmess qft"
				}

			}
, 			{
				"box" : 				{
					"id" : "qft_active",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 900.0, 580.0, 180.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 944.0, 439.0, 180.0, 22.0 ],
					"text" : "ACTIVE: qft"
				}

			}
, 			{
				"box" : 				{
					"id" : "qft_active_prepend",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1080.0, 550.0, 135.0, 22.0 ],
					"text" : "prepend set ACTIVE:"
				}

			}
 ],
		"lines" : [ 			{
				"patchline" : 				{
					"destination" : [ "rotation_layer", 0 ],
					"order" : 0,
					"source" : [ "axis_rx", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "theta_qasm", 0 ],
					"order" : 1,
					"source" : [ "axis_rx", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "rotation_layer", 0 ],
					"order" : 0,
					"source" : [ "axis_ry", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "theta_qasm", 0 ],
					"order" : 1,
					"source" : [ "axis_ry", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "rotation_layer", 0 ],
					"order" : 0,
					"source" : [ "axis_rz", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "theta_qasm", 0 ],
					"order" : 1,
					"source" : [ "axis_rz", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "controls_unpack", 0 ],
					"source" : [ "controls_slice", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "correlation_display", 0 ],
					"order" : 1,
					"source" : [ "controls_unpack", 2 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "entanglement_display", 0 ],
					"order" : 1,
					"source" : [ "controls_unpack", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "entropy_display", 0 ],
					"order" : 1,
					"source" : [ "controls_unpack", 3 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "entropy_sig", 0 ],
					"order" : 0,
					"source" : [ "controls_unpack", 3 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "gain_map", 0 ],
					"order" : 0,
					"source" : [ "controls_unpack", 2 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "pitch_map", 0 ],
					"order" : 0,
					"source" : [ "controls_unpack", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "polarization_display", 0 ],
					"order" : 1,
					"source" : [ "controls_unpack", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "scan_map", 0 ],
					"order" : 0,
					"source" : [ "controls_unpack", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "xx", 0 ],
					"source" : [ "corr_unpack", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "yy", 0 ],
					"source" : [ "corr_unpack", 2 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "zz", 0 ],
					"source" : [ "corr_unpack", 3 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "designer_status", 0 ],
					"source" : [ "designer", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "qac", 0 ],
					"source" : [ "designer", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "y_depth_mul", 1 ],
					"source" : [ "entropy_sig", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "phasor", 0 ],
					"source" : [ "freq", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "dac", 1 ],
					"order" : 0,
					"source" : [ "gain", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "dac", 0 ],
					"order" : 1,
					"source" : [ "gain", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "gain", 1 ],
					"source" : [ "gain_map", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "gain_map", 2 ],
					"source" : [ "gain_max", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "gain_max", 0 ],
					"source" : [ "gain_max_default", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "gain_map", 1 ],
					"source" : [ "gain_min", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "gain_min", 0 ],
					"source" : [ "gain_min_default", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "ir_ibm_mul", 0 ],
					"source" : [ "ir_convolver", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "ir_local_mul", 0 ],
					"source" : [ "ir_convolver", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "ir_dry_sqrt", 0 ],
					"source" : [ "ir_dry_inverse", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "ir_dry_mul", 1 ],
					"source" : [ "ir_dry_sqrt", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "ir_drywet_pack", 0 ],
					"source" : [ "ir_drywet", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "ir_dry_inverse", 0 ],
					"order" : 1,
					"source" : [ "ir_drywet_line", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "ir_wet_sqrt", 0 ],
					"order" : 0,
					"source" : [ "ir_drywet_line", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "ir_drywet_line", 0 ],
					"source" : [ "ir_drywet_pack", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "ir_wet_sum", 1 ],
					"source" : [ "ir_ibm_mul", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "ir_wet_sum", 0 ],
					"source" : [ "ir_local_mul", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "gain", 0 ],
					"source" : [ "ir_mix_sum", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "ir_convolver", 0 ],
					"source" : [ "ir_set_ibm", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "ir_convolver", 0 ],
					"source" : [ "ir_set_local", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "ir_mix_sum", 1 ],
					"source" : [ "ir_wet_mul", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "ir_wet_mul", 1 ],
					"source" : [ "ir_wet_sqrt", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "ir_wet_mul", 0 ],
					"source" : [ "ir_wet_sum", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "display", 0 ],
					"source" : [ "loader", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "status", 0 ],
					"source" : [ "loader", 2 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "dac", 1 ],
					"order" : 0,
					"source" : [ "local_monitor_gain", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "dac", 0 ],
					"order" : 1,
					"source" : [ "local_monitor_gain", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-5", 0 ],
					"source" : [ "morph", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "y_depth_mul", 0 ],
					"source" : [ "obj-5", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "controls_slice", 0 ],
					"source" : [ "oroute", 6 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "corr_unpack", 0 ],
					"source" : [ "oroute", 3 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "loader", 0 ],
					"source" : [ "oroute", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "pauli_slice", 0 ],
					"order" : 0,
					"source" : [ "oroute", 4 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "print", 0 ],
					"source" : [ "oroute", 8 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "status", 0 ],
					"source" : [ "oroute", 2 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "status", 0 ],
					"source" : [ "oroute", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "surface_loader", 0 ],
					"order" : 1,
					"source" : [ "oroute", 4 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "surface_slice", 0 ],
					"source" : [ "oroute", 5 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "v3_renderer", 0 ],
					"source" : [ "oroute", 7 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "pauli_display", 0 ],
					"source" : [ "pauli_slice", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "two_d", 0 ],
					"order" : 1,
					"source" : [ "phasor", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "v3_ibm_wave", 0 ],
					"order" : 0,
					"source" : [ "phasor", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "v3_local_wave", 0 ],
					"order" : 2,
					"source" : [ "phasor", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "freq", 0 ],
					"source" : [ "pitch_map", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "rotation_layer", 0 ],
					"source" : [ "qac", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "qft_active", 0 ],
					"source" : [ "qft_active_prepend", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "qft_active_prepend", 0 ],
					"order" : 0,
					"source" : [ "qft_default", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "qft_pack", 0 ],
					"order" : 1,
					"source" : [ "qft_default", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "qft_active_prepend", 0 ],
					"order" : 0,
					"source" : [ "qft_iqft", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "qft_pack", 0 ],
					"order" : 1,
					"source" : [ "qft_iqft", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "qft_active_prepend", 0 ],
					"order" : 0,
					"source" : [ "qft_none", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "qft_pack", 0 ],
					"order" : 1,
					"source" : [ "qft_none", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "qft_udp", 0 ],
					"source" : [ "qft_pack", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "qft_active_prepend", 0 ],
					"order" : 0,
					"source" : [ "qft_qft", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "qft_pack", 0 ],
					"order" : 1,
					"source" : [ "qft_qft", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "render_detail_prepend", 0 ],
					"source" : [ "render_detail", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "v3_renderer", 0 ],
					"source" : [ "render_detail_prepend", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "v3_renderer", 0 ],
					"source" : [ "render_mode_density", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "v3_renderer", 0 ],
					"source" : [ "render_mode_hybrid", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "v3_renderer", 0 ],
					"source" : [ "render_mode_ifft", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "v3_renderer", 0 ],
					"source" : [ "render_mode_spline", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "render_nonlinear_prepend", 0 ],
					"source" : [ "render_nonlinear", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "v3_renderer", 0 ],
					"source" : [ "render_nonlinear_prepend", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "render_spectral_prepend", 0 ],
					"source" : [ "render_spectral", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "v3_renderer", 0 ],
					"source" : [ "render_spectral_prepend", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "rotation_enable_prepend", 0 ],
					"source" : [ "rotation_enable", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "rotation_enable", 0 ],
					"source" : [ "rotation_enable_default", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "rotation_layer", 0 ],
					"source" : [ "rotation_enable_prepend", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "sender", 0 ],
					"source" : [ "rotation_layer", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "sendstatus", 0 ],
					"source" : [ "rotation_layer", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "rotation_target_prepend", 0 ],
					"source" : [ "rotation_target", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "rotation_layer", 0 ],
					"source" : [ "rotation_target_prepend", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "rotation_layer", 0 ],
					"source" : [ "rotation_theta_prepend", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "two_d", 0 ],
					"order" : 1,
					"source" : [ "rows", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "v3_ibm_wave", 0 ],
					"order" : 0,
					"source" : [ "rows", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "v3_local_wave", 0 ],
					"order" : 2,
					"source" : [ "rows", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "rows", 0 ],
					"source" : [ "rows_load", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "morph", 0 ],
					"source" : [ "scan_map", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "sendstatus", 0 ],
					"source" : [ "sender", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "source_sum", 1 ],
					"source" : [ "source_ibm_mul", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "source_sum", 0 ],
					"source" : [ "source_local_mul", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "ir_convolver", 0 ],
					"order" : 1,
					"source" : [ "source_sum", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "ir_mix_sum", 0 ],
					"order" : 0,
					"source" : [ "source_sum", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "source_xfade_pack", 0 ],
					"source" : [ "source_xfade", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "ir_local_mul", 1 ],
					"order" : 1,
					"source" : [ "source_xfade_inverse", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "source_local_mul", 1 ],
					"order" : 0,
					"source" : [ "source_xfade_inverse", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "ir_ibm_mul", 1 ],
					"order" : 2,
					"source" : [ "source_xfade_line", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "source_ibm_mul", 1 ],
					"order" : 0,
					"source" : [ "source_xfade_line", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "source_xfade_inverse", 0 ],
					"order" : 1,
					"source" : [ "source_xfade_line", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "source_xfade_line", 0 ],
					"source" : [ "source_xfade_pack", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "buffer", 0 ],
					"order" : 1,
					"source" : [ "surface_loader", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "rows", 0 ],
					"order" : 0,
					"source" : [ "surface_loader", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "status", 0 ],
					"source" : [ "surface_loader", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "buffer", 0 ],
					"source" : [ "surface_replace", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "surface_replace", 0 ],
					"source" : [ "surface_slice", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "rotation_theta_prepend", 0 ],
					"order" : 0,
					"source" : [ "theta_control", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "theta_qasm", 0 ],
					"order" : 1,
					"source" : [ "theta_control", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "sender", 0 ],
					"source" : [ "theta_qasm", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "sendstatus", 0 ],
					"source" : [ "theta_qasm", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "theta_qasm", 0 ],
					"source" : [ "theta_send", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "oroute", 0 ],
					"order" : 1,
					"source" : [ "udp", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "rawprint", 0 ],
					"order" : 0,
					"source" : [ "udp", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "source_ibm_mul", 0 ],
					"source" : [ "v3_ibm_wave", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "ibm_xx", 0 ],
					"source" : [ "v3_ibm_xyz_unpack", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "ibm_yy", 0 ],
					"source" : [ "v3_ibm_xyz_unpack", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "ibm_zz", 0 ],
					"source" : [ "v3_ibm_xyz_unpack", 2 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "local_monitor_gain", 0 ],
					"order" : 1,
					"source" : [ "v3_local_wave", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "source_local_mul", 0 ],
					"order" : 0,
					"source" : [ "v3_local_wave", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "xx", 0 ],
					"source" : [ "v3_local_xyz_unpack", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "yy", 0 ],
					"source" : [ "v3_local_xyz_unpack", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "zz", 0 ],
					"source" : [ "v3_local_xyz_unpack", 2 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "display", 0 ],
					"source" : [ "v3_renderer", 3 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "ir_set_ibm", 0 ],
					"order" : 0,
					"source" : [ "v3_renderer", 2 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "ir_set_local", 0 ],
					"order" : 0,
					"source" : [ "v3_renderer", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "pauli_display", 0 ],
					"source" : [ "v3_renderer", 4 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "status", 0 ],
					"source" : [ "v3_renderer", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "v3_ibm_buffer", 0 ],
					"order" : 1,
					"source" : [ "v3_renderer", 2 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "v3_ibm_xyz_unpack", 0 ],
					"source" : [ "v3_renderer", 6 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "v3_local_buffer", 0 ],
					"order" : 1,
					"source" : [ "v3_renderer", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "v3_local_xyz_unpack", 0 ],
					"source" : [ "v3_renderer", 5 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "two_d", 1 ],
					"order" : 0,
					"source" : [ "y_depth_mul", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "v3_ibm_wave", 1 ],
					"order" : 1,
					"source" : [ "y_depth_mul", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "v3_local_wave", 1 ],
					"order" : 2,
					"source" : [ "y_depth_mul", 0 ]
				}

			}
 ],
		"originid" : "pat-44",
		"dependency_cache" : [ 			{
				"name" : "multiconvolve~.mxo",
				"type" : "iLaX"
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
				"name" : "qac_wavetable_sender_v1.maxpat",
				"bootpath" : "~/QuantumSonification/max",
				"patcherrelativepath" : ".",
				"type" : "JSON",
				"implicit" : 1
			}
, 			{
				"name" : "qmw_compact_state_renderer_v4.js",
				"bootpath" : "~/QuantumSonification/max",
				"patcherrelativepath" : ".",
				"type" : "TEXT",
				"implicit" : 1
			}
, 			{
				"name" : "qmw_parameterized_bell_v1.js",
				"bootpath" : "~/QuantumSonification/max",
				"patcherrelativepath" : ".",
				"type" : "TEXT",
				"implicit" : 1
			}
, 			{
				"name" : "qmw_pauli_surface_receiver_v1.js",
				"bootpath" : "~/QuantumSonification/max",
				"patcherrelativepath" : ".",
				"type" : "TEXT",
				"implicit" : 1
			}
, 			{
				"name" : "qmw_qac_wavetable_designer_v1.js",
				"bootpath" : "~/QuantumSonification/max",
				"patcherrelativepath" : ".",
				"type" : "TEXT",
				"implicit" : 1
			}
, 			{
				"name" : "qmw_qasm_rotation_layer_v2.js",
				"bootpath" : "~/QuantumSonification/max",
				"patcherrelativepath" : ".",
				"type" : "TEXT",
				"implicit" : 1
			}
, 			{
				"name" : "qmw_wavetable_receiver_v4.js",
				"bootpath" : "~/QuantumSonification/max",
				"patcherrelativepath" : ".",
				"type" : "TEXT",
				"implicit" : 1
			}
 ],
		"autosave" : 0
	}

}
