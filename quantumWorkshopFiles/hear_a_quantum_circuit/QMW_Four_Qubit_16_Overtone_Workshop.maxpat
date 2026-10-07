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
		"rect" : [ 34.0, 100.0, 1400.0, 816.0 ],
		"openinpresentation" : 1,
		"gridsize" : [ 15.0, 15.0 ],
		"boxes" : [ 			{
				"box" : 				{
					"fontsize" : 26.0,
					"id" : "title",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 24.0, 18.0, 900.0, 36.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 24.0, 18.0, 900.0, 36.0 ],
					"text" : "FROM TWO QUBITS TO FOUR · 16-OVERTONE ADDITIVE SYNTH",
					"textcolor" : [ 0.9, 0.93, 0.97, 1.0 ]
				}

			}
, 			{
				"box" : 				{
					"fontsize" : 14.0,
					"id" : "subtitle",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 24.0, 55.0, 1050.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 24.0, 55.0, 1050.0, 22.0 ],
					"text" : "Build a four-qubit circuit. BUILD + HEAR calculates 16 basis probabilities; each basis state controls one harmonic partial.",
					"textcolor" : [ 0.51, 0.81, 1.0, 1.0 ]
				}

			}
, 			{
				"box" : 				{
					"filename" : "qmw_qac_circuit_programmer_v1.js",
					"id" : "qac-ui",
					"jsarguments" : [ "qmw_qac_circuit_programmer_v1.js" ],
					"maxclass" : "jsui",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 24.0, 88.0, 780.0, 390.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 24.0, 88.0, 780.0, 390.0 ]
				}

			}
, 			{
				"box" : 				{
					"fontsize" : 12.0,
					"id" : "qac-status-label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 24.0, 490.0, 60.0, 20.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 24.0, 490.0, 60.0, 20.0 ],
					"text" : "CIRCUIT",
					"textcolor" : [ 0.51, 0.81, 1.0, 1.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "qac-status",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 90.0, 488.0, 470.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 90.0, 488.0, 470.0, 22.0 ],
					"text" : "Choose a preset or place gates, then click BUILD + HEAR."
				}

			}
, 			{
				"box" : 				{
					"id" : "adapter",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "" ],
					"patching_rect" : [ 24.0, 540.0, 265.0, 22.0 ],
					"saved_object_attributes" : 					{
						"filename" : "qmw_qac_to_16_probabilities_workshop.js",
						"parameter_enable" : 0
					}
,
					"text" : "js qmw_qac_to_16_probabilities_workshop.js"
				}

			}
, 			{
				"box" : 				{
					"id" : "adapter-status",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 300.0, 540.0, 220.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 826.0, 405.0, 250.0, 22.0 ],
					"text" : "0 gates -> 1 active overtone"
				}

			}
, 			{
				"box" : 				{
					"id" : "state-split",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "" ],
					"patching_rect" : [ 24.0, 580.0, 42.0, 22.0 ],
					"text" : "t l l"
				}

			}
, 			{
				"box" : 				{
					"id" : "slider-set",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 84.0, 580.0, 78.0, 22.0 ],
					"text" : "prepend setlist"
				}

			}
, 			{
				"box" : 				{
					"fontsize" : 18.0,
					"id" : "probability-title",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 826.0, 98.0, 500.0, 27.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 826.0, 98.0, 500.0, 27.0 ],
					"text" : "16 BASIS STATES → 16 HARMONIC PARTIALS",
					"textcolor" : [ 0.9, 0.93, 0.97, 1.0 ]
				}

			}
, 			{
				"box" : 				{
					"fontsize" : 12.0,
					"id" : "mapping-note",
					"linecount" : 2,
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 826.0, 130.0, 530.0, 35.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 826.0, 130.0, 606.0, 23.0 ],
					"text" : "|0000〉 controls partial 1; |1111〉 controls partial 16. Probability controls power; amplitude uses sqrt(probability).",
					"textcolor" : [ 0.57, 0.62, 0.69, 1.0 ]
				}

			}
, 			{
				"box" : 				{
					"bgcolor" : [ 0.09, 0.12, 0.16, 1.0 ],
					"contdata" : 1,
					"id" : "probabilities",
					"maxclass" : "multislider",
					"numinlets" : 1,
					"numoutlets" : 2,
					"orientation" : 0,
					"outlettype" : [ "", "" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 826.0, 176.0, 530.0, 145.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 826.0, 176.0, 530.0, 145.0 ],
					"setminmax" : [ 0.0, 1.0 ],
					"setstyle" : 1,
					"size" : 16,
					"slidercolor" : [ 0.27, 0.54, 1.0, 1.0 ]
				}

			}
, 			{
				"box" : 				{
					"fontsize" : 11.0,
					"id" : "partial-labels",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 826.0, 325.0, 530.0, 19.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 826.0, 325.0, 530.0, 19.0 ],
					"text" : "partial     1       2       3       4       5       6       7       8       9      10      11      12      13      14      15      16",
					"textcolor" : [ 0.57, 0.62, 0.69, 1.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "synth-helper",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 3,
					"outlettype" : [ "", "", "" ],
					"patching_rect" : [ 220.0, 620.0, 205.0, 22.0 ],
					"saved_object_attributes" : 					{
						"filename" : "qmw_16_overtone_workshop.js",
						"parameter_enable" : 0
					}
,
					"text" : "js qmw_16_overtone_workshop.js"
				}

			}
, 			{
				"box" : 				{
					"id" : "synth-status",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 440.0, 620.0, 240.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 1085.0, 405.0, 270.0, 22.0 ],
					"text" : "Active basis states: |0000>"
				}

			}
, 			{
				"box" : 				{
					"id" : "poly-synth",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 220.0, 660.0, 285.0, 22.0 ],
					"text" : "poly~ qmw_16_overtone_voice 16 @parallel 1"
				}

			}
, 			{
				"box" : 				{
					"id" : "safe-scale",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 220.0, 700.0, 58.0, 22.0 ],
					"text" : "*~ 0.12"
				}

			}
, 			{
				"box" : 				{
					"id" : "linear-pass",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 220.0, 738.0, 48.0, 22.0 ],
					"text" : "*~ 1."
				}

			}
, 			{
				"box" : 				{
					"id" : "master-multiply",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 220.0, 776.0, 36.0, 22.0 ],
					"text" : "*~"
				}

			}
, 			{
				"box" : 				{
					"fontsize" : 13.0,
					"id" : "fundamental-label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 826.0, 365.0, 130.0, 21.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 826.0, 365.0, 130.0, 21.0 ],
					"text" : "FUNDAMENTAL Hz",
					"textcolor" : [ 0.51, 0.81, 1.0, 1.0 ]
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "fundamental",
					"maxclass" : "flonum",
					"maximum" : 220.0,
					"minimum" : 20.0,
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 960.0, 365.0, 70.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 960.0, 365.0, 70.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "fundamental-prepend",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 700.0, 620.0, 132.0, 22.0 ],
					"text" : "prepend fundamental"
				}

			}
, 			{
				"box" : 				{
					"id" : "fundamental-default",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 700.0, 580.0, 82.0, 22.0 ],
					"text" : "loadmess 55."
				}

			}
, 			{
				"box" : 				{
					"fontsize" : 13.0,
					"id" : "master-label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 1050.0, 365.0, 68.0, 21.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 1050.0, 365.0, 68.0, 21.0 ],
					"text" : "MASTER",
					"textcolor" : [ 0.51, 0.81, 1.0, 1.0 ]
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "master",
					"maxclass" : "flonum",
					"maximum" : 1.0,
					"minimum" : 0.0,
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 1120.0, 365.0, 62.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 1120.0, 365.0, 62.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "master-pack",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 540.0, 700.0, 78.0, 22.0 ],
					"text" : "pack 0. 40"
				}

			}
, 			{
				"box" : 				{
					"id" : "master-line",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 2,
					"outlettype" : [ "signal", "bang" ],
					"patching_rect" : [ 540.0, 738.0, 40.0, 22.0 ],
					"text" : "line~"
				}

			}
, 			{
				"box" : 				{
					"id" : "master-default",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 540.0, 660.0, 86.0, 22.0 ],
					"text" : "loadmess 0.8"
				}

			}
, 			{
				"box" : 				{
					"fontsize" : 13.0,
					"id" : "dsp-label",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 1200.0, 365.0, 58.0, 21.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 1200.0, 365.0, 58.0, 21.0 ],
					"text" : "AUDIO",
					"textcolor" : [ 0.51, 0.81, 1.0, 1.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "dsp-toggle",
					"maxclass" : "toggle",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "int" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 1260.0, 363.0, 26.0, 26.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 1260.0, 363.0, 26.0, 26.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "dac",
					"maxclass" : "ezdac~",
					"numinlets" : 2,
					"numoutlets" : 0,
					"patching_rect" : [ 300.0, 776.0, 45.0, 45.0 ]
				}

			}
, 			{
				"box" : 				{
					"fontsize" : 15.0,
					"id" : "spectrum-title",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 826.0, 650.0, 500.0, 23.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 826.0, 650.0, 500.0, 23.0 ],
					"text" : "SUMMED OUTPUT SPECTRUM · all 16 partials · 55–880 Hz",
					"textcolor" : [ 0.9, 0.93, 0.97, 1.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "spectrum",
					"maxclass" : "spectroscope~",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 826.0, 677.0, 530.0, 140.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 826.0, 677.0, 530.0, 140.0 ]
				}

			}
, 			{
				"box" : 				{
					"fontsize" : 13.0,
					"id" : "footer",
					"linecount" : 3,
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 24.0, 538.0, 720.0, 50.0 ],
					"presentation" : 1,
					"presentation_linecount" : 2,
					"presentation_rect" : [ 24.0, 538.0, 760.0, 36.0 ],
					"text" : "Mapping choice: partial k = 55 × k Hz. The circuit does not literally contain overtones; this additive instrument makes its 16-dimensional probability distribution audible. Advanced QMW density, operator, and wavetable engines remain backstage.",
					"textcolor" : [ 0.57, 0.62, 0.69, 1.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "initial-state",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 24.0, 620.0, 310.0, 22.0 ],
					"text" : "loadmess 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0"
				}

			}
, 			{
				"box" : 				{
					"id" : "local-state-input",
					"maxclass" : "newobj",
					"numinlets" : 0,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 24.0, 660.0, 205.0, 22.0 ],
					"text" : "r qmw.workshop.4q.probabilities"
				}

			}
, 			{
				"box" : 				{
					"id" : "qac-print",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 24.0, 700.0, 121.0, 22.0 ],
					"text" : "print QMW_4Q_QAC"
				}

			}
, 			{
				"box" : 				{
					"fontsize" : 15.0,
					"id" : "gain-title",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 826.0, 442.0, 500.0, 23.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 826.0, 442.0, 500.0, 23.0 ],
					"text" : "INDIVIDUAL PARTIAL GAINS · √probability · AUDIO ON",
					"textcolor" : [ 0.9, 0.93, 0.97, 1.0 ]
				}

			}
, 			{
				"box" : 				{
					"fontsize" : 11.0,
					"id" : "gain-note",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 826.0, 462.0, 500.0, 19.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 826.0, 462.0, 500.0, 19.0 ],
					"text" : "Each meter shows one oscillator gain before the voices are summed.",
					"textcolor" : [ 0.57, 0.62, 0.69, 1.0 ]
				}

			}
, 			{
				"box" : 				{
					"fontname" : "Menlo",
					"fontsize" : 10.0,
					"id" : "gain-labels",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 832.0, 609.0, 520.0, 18.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 832.0, 609.0, 520.0, 18.0 ],
					"text" : " 1     2    3    4    5    6    7    8     9   10    11   12   13   14   15   16",
					"textcolor" : [ 0.57, 0.62, 0.69, 1.0 ]
				}

			}
, 			{
				"box" : 				{
					"fontname" : "Menlo",
					"fontsize" : 7.5,
					"id" : "ket-label-1",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 830.0, 624.0, 39.0, 17.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 830.0, 624.0, 39.0, 17.0 ],
					"text" : "|0000〉",
					"textcolor" : [ 0.51, 0.81, 1.0, 1.0 ],
					"textjustification" : 1
				}

			}
, 			{
				"box" : 				{
					"fontname" : "Menlo",
					"fontsize" : 7.5,
					"id" : "ket-label-2",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 861.0, 624.0, 39.0, 17.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 861.0, 624.0, 39.0, 17.0 ],
					"text" : "|0001〉",
					"textcolor" : [ 0.51, 0.81, 1.0, 1.0 ],
					"textjustification" : 1
				}

			}
, 			{
				"box" : 				{
					"fontname" : "Menlo",
					"fontsize" : 7.5,
					"id" : "ket-label-3",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 892.0, 624.0, 39.0, 17.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 892.0, 624.0, 39.0, 17.0 ],
					"text" : "|0010〉",
					"textcolor" : [ 0.51, 0.81, 1.0, 1.0 ],
					"textjustification" : 1
				}

			}
, 			{
				"box" : 				{
					"fontname" : "Menlo",
					"fontsize" : 7.5,
					"id" : "ket-label-4",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 923.0, 624.0, 39.0, 17.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 923.0, 624.0, 39.0, 17.0 ],
					"text" : "|0011〉",
					"textcolor" : [ 0.51, 0.81, 1.0, 1.0 ],
					"textjustification" : 1
				}

			}
, 			{
				"box" : 				{
					"fontname" : "Menlo",
					"fontsize" : 7.5,
					"id" : "ket-label-5",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 954.0, 624.0, 39.0, 17.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 954.0, 624.0, 39.0, 17.0 ],
					"text" : "|0100〉",
					"textcolor" : [ 0.51, 0.81, 1.0, 1.0 ],
					"textjustification" : 1
				}

			}
, 			{
				"box" : 				{
					"fontname" : "Menlo",
					"fontsize" : 7.5,
					"id" : "ket-label-6",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 985.0, 624.0, 39.0, 17.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 985.0, 624.0, 39.0, 17.0 ],
					"text" : "|0101〉",
					"textcolor" : [ 0.51, 0.81, 1.0, 1.0 ],
					"textjustification" : 1
				}

			}
, 			{
				"box" : 				{
					"fontname" : "Menlo",
					"fontsize" : 7.5,
					"id" : "ket-label-7",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 1016.0, 624.0, 39.0, 17.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 1016.0, 624.0, 39.0, 17.0 ],
					"text" : "|0110〉",
					"textcolor" : [ 0.51, 0.81, 1.0, 1.0 ],
					"textjustification" : 1
				}

			}
, 			{
				"box" : 				{
					"fontname" : "Menlo",
					"fontsize" : 7.5,
					"id" : "ket-label-8",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 1047.0, 624.0, 39.0, 17.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 1047.0, 624.0, 39.0, 17.0 ],
					"text" : "|0111〉",
					"textcolor" : [ 0.51, 0.81, 1.0, 1.0 ],
					"textjustification" : 1
				}

			}
, 			{
				"box" : 				{
					"fontname" : "Menlo",
					"fontsize" : 7.5,
					"id" : "ket-label-9",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 1078.0, 624.0, 39.0, 17.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 1078.0, 624.0, 39.0, 17.0 ],
					"text" : "|1000〉",
					"textcolor" : [ 0.51, 0.81, 1.0, 1.0 ],
					"textjustification" : 1
				}

			}
, 			{
				"box" : 				{
					"fontname" : "Menlo",
					"fontsize" : 7.5,
					"id" : "ket-label-10",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 1109.0, 624.0, 39.0, 17.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 1109.0, 624.0, 39.0, 17.0 ],
					"text" : "|1001〉",
					"textcolor" : [ 0.51, 0.81, 1.0, 1.0 ],
					"textjustification" : 1
				}

			}
, 			{
				"box" : 				{
					"fontname" : "Menlo",
					"fontsize" : 7.5,
					"id" : "ket-label-11",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 1140.0, 624.0, 39.0, 17.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 1140.0, 624.0, 39.0, 17.0 ],
					"text" : "|1010〉",
					"textcolor" : [ 0.51, 0.81, 1.0, 1.0 ],
					"textjustification" : 1
				}

			}
, 			{
				"box" : 				{
					"fontname" : "Menlo",
					"fontsize" : 7.5,
					"id" : "ket-label-12",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 1171.0, 624.0, 39.0, 17.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 1171.0, 624.0, 39.0, 17.0 ],
					"text" : "|1011〉",
					"textcolor" : [ 0.51, 0.81, 1.0, 1.0 ],
					"textjustification" : 1
				}

			}
, 			{
				"box" : 				{
					"fontname" : "Menlo",
					"fontsize" : 7.5,
					"id" : "ket-label-13",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 1202.0, 624.0, 39.0, 17.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 1202.0, 624.0, 39.0, 17.0 ],
					"text" : "|1100〉",
					"textcolor" : [ 0.51, 0.81, 1.0, 1.0 ],
					"textjustification" : 1
				}

			}
, 			{
				"box" : 				{
					"fontname" : "Menlo",
					"fontsize" : 7.5,
					"id" : "ket-label-14",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 1233.0, 624.0, 39.0, 17.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 1233.0, 624.0, 39.0, 17.0 ],
					"text" : "|1101〉",
					"textcolor" : [ 0.51, 0.81, 1.0, 1.0 ],
					"textjustification" : 1
				}

			}
, 			{
				"box" : 				{
					"fontname" : "Menlo",
					"fontsize" : 7.5,
					"id" : "ket-label-15",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 1264.0, 624.0, 39.0, 17.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 1264.0, 624.0, 39.0, 17.0 ],
					"text" : "|1110〉",
					"textcolor" : [ 0.51, 0.81, 1.0, 1.0 ],
					"textjustification" : 1
				}

			}
, 			{
				"box" : 				{
					"fontname" : "Menlo",
					"fontsize" : 7.5,
					"id" : "ket-label-16",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 1295.0, 624.0, 39.0, 17.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 1295.0, 624.0, 39.0, 17.0 ],
					"text" : "|1111〉",
					"textcolor" : [ 0.51, 0.81, 1.0, 1.0 ],
					"textjustification" : 1
				}

			}
, 			{
				"box" : 				{
					"id" : "gain-unpack",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 16,
					"outlettype" : [ "float", "float", "float", "float", "float", "float", "float", "float", "float", "float", "float", "float", "float", "float", "float", "float" ],
					"patching_rect" : [ 850.0, 850.0, 470.0, 22.0 ],
					"text" : "unpack 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0."
				}

			}
, 			{
				"box" : 				{
					"id" : "gain-sig-1",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 850.0, 890.0, 36.0, 22.0 ],
					"text" : "sig~"
				}

			}
, 			{
				"box" : 				{
					"id" : "gain-sig-2",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 881.0, 920.0, 36.0, 22.0 ],
					"text" : "sig~"
				}

			}
, 			{
				"box" : 				{
					"id" : "gain-sig-3",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 912.0, 890.0, 36.0, 22.0 ],
					"text" : "sig~"
				}

			}
, 			{
				"box" : 				{
					"id" : "gain-sig-4",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 943.0, 920.0, 36.0, 22.0 ],
					"text" : "sig~"
				}

			}
, 			{
				"box" : 				{
					"id" : "gain-sig-5",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 974.0, 890.0, 36.0, 22.0 ],
					"text" : "sig~"
				}

			}
, 			{
				"box" : 				{
					"id" : "gain-sig-6",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 1005.0, 920.0, 36.0, 22.0 ],
					"text" : "sig~"
				}

			}
, 			{
				"box" : 				{
					"id" : "gain-sig-7",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 1036.0, 890.0, 36.0, 22.0 ],
					"text" : "sig~"
				}

			}
, 			{
				"box" : 				{
					"id" : "gain-sig-8",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 1067.0, 920.0, 36.0, 22.0 ],
					"text" : "sig~"
				}

			}
, 			{
				"box" : 				{
					"id" : "gain-sig-9",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 1098.0, 890.0, 36.0, 22.0 ],
					"text" : "sig~"
				}

			}
, 			{
				"box" : 				{
					"id" : "gain-sig-10",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 1129.0, 920.0, 36.0, 22.0 ],
					"text" : "sig~"
				}

			}
, 			{
				"box" : 				{
					"id" : "gain-sig-11",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 1160.0, 890.0, 36.0, 22.0 ],
					"text" : "sig~"
				}

			}
, 			{
				"box" : 				{
					"id" : "gain-sig-12",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 1191.0, 920.0, 36.0, 22.0 ],
					"text" : "sig~"
				}

			}
, 			{
				"box" : 				{
					"id" : "gain-sig-13",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 1222.0, 890.0, 36.0, 22.0 ],
					"text" : "sig~"
				}

			}
, 			{
				"box" : 				{
					"id" : "gain-sig-14",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 1253.0, 920.0, 36.0, 22.0 ],
					"text" : "sig~"
				}

			}
, 			{
				"box" : 				{
					"id" : "gain-sig-15",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 1284.0, 890.0, 36.0, 22.0 ],
					"text" : "sig~"
				}

			}
, 			{
				"box" : 				{
					"id" : "gain-sig-16",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 1315.0, 920.0, 36.0, 22.0 ],
					"text" : "sig~"
				}

			}
, 			{
				"box" : 				{
					"id" : "gain-meter-1",
					"maxclass" : "meter~",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "float" ],
					"patching_rect" : [ 840.0, 482.0, 18.0, 124.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 840.0, 482.0, 18.0, 124.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "gain-meter-2",
					"maxclass" : "meter~",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "float" ],
					"patching_rect" : [ 871.0, 482.0, 18.0, 124.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 871.0, 482.0, 18.0, 124.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "gain-meter-3",
					"maxclass" : "meter~",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "float" ],
					"patching_rect" : [ 902.0, 482.0, 18.0, 124.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 902.0, 482.0, 18.0, 124.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "gain-meter-4",
					"maxclass" : "meter~",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "float" ],
					"patching_rect" : [ 933.0, 482.0, 18.0, 124.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 933.0, 482.0, 18.0, 124.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "gain-meter-5",
					"maxclass" : "meter~",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "float" ],
					"patching_rect" : [ 964.0, 482.0, 18.0, 124.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 964.0, 482.0, 18.0, 124.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "gain-meter-6",
					"maxclass" : "meter~",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "float" ],
					"patching_rect" : [ 995.0, 482.0, 18.0, 124.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 995.0, 482.0, 18.0, 124.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "gain-meter-7",
					"maxclass" : "meter~",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "float" ],
					"patching_rect" : [ 1026.0, 482.0, 18.0, 124.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 1026.0, 482.0, 18.0, 124.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "gain-meter-8",
					"maxclass" : "meter~",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "float" ],
					"patching_rect" : [ 1057.0, 482.0, 18.0, 124.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 1057.0, 482.0, 18.0, 124.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "gain-meter-9",
					"maxclass" : "meter~",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "float" ],
					"patching_rect" : [ 1088.0, 482.0, 18.0, 124.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 1088.0, 482.0, 18.0, 124.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "gain-meter-10",
					"maxclass" : "meter~",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "float" ],
					"patching_rect" : [ 1119.0, 482.0, 18.0, 124.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 1119.0, 482.0, 18.0, 124.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "gain-meter-11",
					"maxclass" : "meter~",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "float" ],
					"patching_rect" : [ 1150.0, 482.0, 18.0, 124.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 1150.0, 482.0, 18.0, 124.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "gain-meter-12",
					"maxclass" : "meter~",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "float" ],
					"patching_rect" : [ 1181.0, 482.0, 18.0, 124.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 1181.0, 482.0, 18.0, 124.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "gain-meter-13",
					"maxclass" : "meter~",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "float" ],
					"patching_rect" : [ 1212.0, 482.0, 18.0, 124.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 1212.0, 482.0, 18.0, 124.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "gain-meter-14",
					"maxclass" : "meter~",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "float" ],
					"patching_rect" : [ 1243.0, 482.0, 18.0, 124.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 1243.0, 482.0, 18.0, 124.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "gain-meter-15",
					"maxclass" : "meter~",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "float" ],
					"patching_rect" : [ 1274.0, 482.0, 18.0, 124.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 1274.0, 482.0, 18.0, 124.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "gain-meter-16",
					"maxclass" : "meter~",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "float" ],
					"patching_rect" : [ 1305.0, 482.0, 18.0, 124.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 1305.0, 482.0, 18.0, 124.0 ]
			}

			}
, 			{
				"box" : 				{
					"id" : "expected-send",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 700.0, 700.0, 190.0, 22.0 ],
					"text" : "s qmw.workshop.4q.expected"
				}

			}
, 			{
				"box" : 				{
					"id" : "audition-receive",
					"maxclass" : "newobj",
					"numinlets" : 0,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 700.0, 738.0, 190.0, 22.0 ],
					"text" : "r qmw.workshop.4q.audition"
				}

			}
, 			{
				"box" : 				{
					"id" : "synth-control-receive",
					"maxclass" : "newobj",
					"numinlets" : 0,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 700.0, 776.0, 205.0, 22.0 ],
					"text" : "r qmw.workshop.4q.synth.control"
				}

			}
 ],
		"lines" : [ 			{
				"patchline" : 				{
					"destination" : [ "adapter-status", 1 ],
					"source" : [ "adapter", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "state-split", 0 ],
					"source" : [ "adapter", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "expected-send", 0 ],
					"source" : [ "adapter", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "synth-helper", 0 ],
					"source" : [ "audition-receive", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "synth-helper", 0 ],
					"source" : [ "synth-control-receive", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "expected-send", 0 ],
					"source" : [ "initial-state", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "dac", 0 ],
					"source" : [ "dsp-toggle", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "fundamental-prepend", 0 ],
					"source" : [ "fundamental", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "fundamental", 0 ],
					"source" : [ "fundamental-default", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "synth-helper", 0 ],
					"source" : [ "fundamental-prepend", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "gain-meter-1", 0 ],
					"source" : [ "gain-sig-1", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "gain-meter-10", 0 ],
					"source" : [ "gain-sig-10", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "gain-meter-11", 0 ],
					"source" : [ "gain-sig-11", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "gain-meter-12", 0 ],
					"source" : [ "gain-sig-12", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "gain-meter-13", 0 ],
					"source" : [ "gain-sig-13", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "gain-meter-14", 0 ],
					"source" : [ "gain-sig-14", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "gain-meter-15", 0 ],
					"source" : [ "gain-sig-15", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "gain-meter-16", 0 ],
					"source" : [ "gain-sig-16", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "gain-meter-2", 0 ],
					"source" : [ "gain-sig-2", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "gain-meter-3", 0 ],
					"source" : [ "gain-sig-3", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "gain-meter-4", 0 ],
					"source" : [ "gain-sig-4", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "gain-meter-5", 0 ],
					"source" : [ "gain-sig-5", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "gain-meter-6", 0 ],
					"source" : [ "gain-sig-6", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "gain-meter-7", 0 ],
					"source" : [ "gain-sig-7", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "gain-meter-8", 0 ],
					"source" : [ "gain-sig-8", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "gain-meter-9", 0 ],
					"source" : [ "gain-sig-9", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "gain-sig-1", 0 ],
					"source" : [ "gain-unpack", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "gain-sig-10", 0 ],
					"source" : [ "gain-unpack", 9 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "gain-sig-11", 0 ],
					"source" : [ "gain-unpack", 10 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "gain-sig-12", 0 ],
					"source" : [ "gain-unpack", 11 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "gain-sig-13", 0 ],
					"source" : [ "gain-unpack", 12 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "gain-sig-14", 0 ],
					"source" : [ "gain-unpack", 13 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "gain-sig-15", 0 ],
					"source" : [ "gain-unpack", 14 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "gain-sig-16", 0 ],
					"source" : [ "gain-unpack", 15 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "gain-sig-2", 0 ],
					"source" : [ "gain-unpack", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "gain-sig-3", 0 ],
					"source" : [ "gain-unpack", 2 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "gain-sig-4", 0 ],
					"source" : [ "gain-unpack", 3 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "gain-sig-5", 0 ],
					"source" : [ "gain-unpack", 4 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "gain-sig-6", 0 ],
					"source" : [ "gain-unpack", 5 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "gain-sig-7", 0 ],
					"source" : [ "gain-unpack", 6 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "gain-sig-8", 0 ],
					"source" : [ "gain-unpack", 7 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "gain-sig-9", 0 ],
					"source" : [ "gain-unpack", 8 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "state-split", 0 ],
					"source" : [ "initial-state", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "state-split", 0 ],
					"source" : [ "local-state-input", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "master-pack", 0 ],
					"source" : [ "master", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "master", 0 ],
					"source" : [ "master-default", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "master-multiply", 1 ],
					"source" : [ "master-line", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "dac", 1 ],
					"order" : 1,
					"source" : [ "master-multiply", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "dac", 0 ],
					"order" : 2,
					"source" : [ "master-multiply", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "spectrum", 0 ],
					"order" : 0,
					"source" : [ "master-multiply", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "master-line", 0 ],
					"source" : [ "master-pack", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "safe-scale", 0 ],
					"source" : [ "poly-synth", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "synth-helper", 0 ],
					"source" : [ "probabilities", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "adapter", 0 ],
					"order" : 1,
					"source" : [ "qac-ui", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "qac-print", 0 ],
					"order" : 0,
					"source" : [ "qac-ui", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "qac-status", 1 ],
					"source" : [ "qac-ui", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "linear-pass", 0 ],
					"source" : [ "safe-scale", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "probabilities", 0 ],
					"source" : [ "slider-set", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "master-multiply", 0 ],
					"source" : [ "linear-pass", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "slider-set", 0 ],
					"source" : [ "state-split", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "synth-helper", 0 ],
					"source" : [ "state-split", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "gain-unpack", 0 ],
					"source" : [ "synth-helper", 2 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "poly-synth", 0 ],
					"source" : [ "synth-helper", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "synth-status", 1 ],
					"source" : [ "synth-helper", 1 ]
				}

			}
 ],
		"originid" : "pat-132",
		"dependency_cache" : [ 			{
				"name" : "qmw_16_overtone_voice.maxpat",
				"bootpath" : "~/QuantumSonification/worktrees/QuantumSonification/workshops/hear_a_quantum_circuit",
				"patcherrelativepath" : ".",
				"type" : "JSON",
				"implicit" : 1
			}
, 			{
				"name" : "qmw_16_overtone_workshop.js",
				"bootpath" : "~/QuantumSonification/worktrees/QuantumSonification/workshops/hear_a_quantum_circuit",
				"patcherrelativepath" : ".",
				"type" : "TEXT",
				"implicit" : 1
			}
, 			{
				"name" : "qmw_qac_circuit_programmer_v1.js",
				"bootpath" : "~/QuantumSonification/worktrees/QuantumSonification/workshops/hear_a_quantum_circuit",
				"patcherrelativepath" : ".",
				"type" : "TEXT",
				"implicit" : 1
			}
, 			{
				"name" : "qmw_qac_to_16_probabilities_workshop.js",
				"bootpath" : "~/QuantumSonification/worktrees/QuantumSonification/workshops/hear_a_quantum_circuit",
				"patcherrelativepath" : ".",
				"type" : "TEXT",
				"implicit" : 1
			}
 ],
		"autosave" : 0,
		"bgcolor" : [ 0.055, 0.075, 0.105, 1.0 ]
	}

}
