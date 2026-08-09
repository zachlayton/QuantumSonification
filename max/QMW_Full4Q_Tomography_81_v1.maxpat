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
		"rect" : [ 128.0, 297.0, 1440.0, 816.0 ],
		"gridsize" : [ 15.0, 15.0 ],
		"boxes" : [ 			{
				"box" : 				{
					"fontsize" : 20.0,
					"id" : "title",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 28.0, 18.0, 920.0, 29.0 ],
					"text" : "QMW · FULL FOUR-QUBIT TOMOGRAPHY · LOCAL ↔ IBM INSTRUMENT v2",
					"textcolor" : [ 0.12, 0.82, 0.92, 1.0 ]
				}

			}
, 			{
				"box" : 				{
					"fontsize" : 13.0,
					"id" : "subtitle",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 30.0, 54.0, 1180.0, 21.0 ],
					"text" : "3⁴ X/Y/Z measurement settings × 2⁴ basis bins × 256 shots = 20,736 events per source. Preserve LOCAL and IBM simultaneously, then crossfade the complete score."
				}

			}
, 			{
				"box" : 				{
					"fontsize" : 11.0,
					"id" : "launch",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 30.0, 94.0, 1280.0, 19.0 ],
					"text" : "Start Python from workshop_lightweight:  /Users/zlayton/miniconda3/envs/music/bin/python qmw_full4q_tomography_osc_v1.py --save-dir /Users/zlayton/QuantumSonification/full4q_tomography_v1/runs",
					"textcolor" : [ 0.7, 0.72, 0.76, 1.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "ghz",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 30.0, 132.0, 130.0, 22.0 ],
					"text" : "ghz none 256 23"
				}

			}
, 			{
				"box" : 				{
					"id" : "ghzqft",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 170.0, 132.0, 130.0, 22.0 ],
					"text" : "ghz qft 256 23"
				}

			}
, 			{
				"box" : 				{
					"id" : "bell",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 310.0, 132.0, 130.0, 22.0 ],
					"text" : "bell none 256 23"
				}

			}
, 			{
				"box" : 				{
					"id" : "weave",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 450.0, 132.0, 140.0, 22.0 ],
					"text" : "weave none 256 23"
				}

			}
, 			{
				"box" : 				{
					"fontsize" : 11.0,
					"id" : "runlabel",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 30.0, 160.0, 550.0, 19.0 ],
					"text" : "Edit any message as preset  transform  shots  seed, then click it."
				}

			}
, 			{
				"box" : 				{
					"id" : "opack_run",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "FullPacket" ],
					"patching_rect" : [ 612.0, 132.0, 194.0, 22.0 ],
					"text" : "o.pack /qmw/tomography/run"
				}

			}
, 			{
				"box" : 				{
					"id" : "udpsend",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 822.0, 132.0, 160.0, 22.0 ],
					"text" : "udpsend 127.0.0.1 7425"
				}

			}
, 			{
				"box" : 				{
					"id" : "pingbutton",
					"maxclass" : "button",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 1000.0, 132.0, 24.0, 24.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "opack_ping",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "FullPacket" ],
					"patching_rect" : [ 1034.0, 132.0, 196.0, 22.0 ],
					"text" : "o.pack /qmw/tomography/ping"
				}

			}
, 			{
				"box" : 				{
					"fontsize" : 10.0,
					"id" : "pinglabel",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 995.0, 158.0, 240.0, 18.0 ],
					"text" : "ping Python service"
				}

			}
, 			{
				"box" : 				{
					"id" : "status",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 30.0, 188.0, 1200.0, 23.0 ],
					"text" : "\"LOCAL✓  IBM✓  mix 0.500  setting 40.500/80  YYYY → YYYZ  row morph 0.500\""
				}

			}
, 			{
				"box" : 				{
					"fontsize" : 12.0,
					"id" : "heatlabel",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 30.0, 226.0, 560.0, 20.0 ],
					"text" : "THE 81-SETTING SCORE · each row is one XXXX…ZZZZ setting; 16 basis bins across",
					"textcolor" : [ 0.9, 0.72, 0.22, 1.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "heatmap",
					"maxclass" : "jit.pwindow",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "jit_matrix", "" ],
					"patching_rect" : [ 30.0, 254.0, 560.0, 390.0 ],
					"sync" : 1
				}

			}
, 			{
				"box" : 				{
					"fontsize" : 12.0,
					"id" : "selectlabel",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 625.0, 226.0, 185.0, 20.0 ],
					"text" : "SETTING POSITION (0–80)",
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
					"patching_rect" : [ 625.0, 254.0, 72.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "prepend_select",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 712.0, 254.0, 96.0, 22.0 ],
					"text" : "prepend select"
				}

			}
, 			{
				"box" : 				{
					"fontsize" : 12.0,
					"id" : "mixlabel",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 820.0, 226.0, 420.0, 20.0 ],
					"text" : "LOCAL  ←  COMPLETE-DATA CROSSFADE  →  IBM",
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
					"patching_rect" : [ 820.0, 254.0, 92.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "prepend_xfade",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 926.0, 254.0, 106.0, 22.0 ],
					"text" : "prepend xfade"
				}

			}
, 			{
				"box" : 				{
					"fontsize" : 11.0,
					"id" : "mixhelp",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 1044.0, 254.0, 285.0, 19.0 ],
					"text" : "0.000 = local     1.000 = IBM"
				}

			}
, 			{
				"box" : 				{
					"fontsize" : 11.0,
					"id" : "histlabel",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 625.0, 292.0, 500.0, 19.0 ],
					"text" : "Interpolated setting: 16 measured basis-state probabilities"
				}

			}
, 			{
				"box" : 				{
					"bgcolor" : [ 0.08, 0.09, 0.12, 1.0 ],
					"id" : "histogram",
					"maxclass" : "multislider",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 625.0, 318.0, 755.0, 140.0 ],
					"setminmax" : [ 0.0, 1.0 ],
					"setstyle" : 1,
					"size" : 16,
					"slidercolor" : [ 0.12, 0.82, 0.92, 1.0 ]
				}

			}
, 			{
				"box" : 				{
					"fontsize" : 11.0,
					"id" : "paulilabel",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 625.0, 476.0, 740.0, 19.0 ],
					"text" : "THE 255 NON-IDENTITY PAULI COEFFICIENTS · IIXY…ZZZZ",
					"textcolor" : [ 0.9, 0.72, 0.22, 1.0 ]
				}

			}
, 			{
				"box" : 				{
					"bgcolor" : [ 0.08, 0.09, 0.12, 1.0 ],
					"id" : "paulis",
					"maxclass" : "multislider",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 625.0, 502.0, 755.0, 142.0 ],
					"setstyle" : 1,
					"size" : 255,
					"slidercolor" : [ 0.78, 0.32, 0.88, 1.0 ]
				}

			}
, 			{
				"box" : 				{
					"fontsize" : 11.0,
					"id" : "shelllabel",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 625.0, 662.0, 680.0, 19.0 ],
					"text" : "CORRELATION-WEIGHT SHELLS · weights 0–4 contain 1, 12, 54, 108, 81 terms",
					"textcolor" : [ 0.9, 0.72, 0.22, 1.0 ]
				}

			}
, 			{
				"box" : 				{
					"bgcolor" : [ 0.08, 0.09, 0.12, 1.0 ],
					"id" : "shells",
					"maxclass" : "multislider",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 625.0, 688.0, 500.0, 96.0 ],
					"setminmax" : [ 0.0, 1.0 ],
					"setstyle" : 1,
					"size" : 5,
					"slidercolor" : [ 0.96, 0.56, 0.18, 1.0 ]
				}

			}
, 			{
				"box" : 				{
					"fontsize" : 11.0,
					"id" : "audiolabel",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 30.0, 664.0, 520.0, 19.0 ],
					"text" : "SONIFY THE CONTINUOUS ROW MORPH · 16 probabilities become harmonic amplitudes",
					"textcolor" : [ 0.9, 0.72, 0.22, 1.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "buffer",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "float", "bang" ],
					"patching_rect" : [ 30.0, 694.0, 248.0, 22.0 ],
					"text" : "buffer~ qmw_full4q_setting @samps 256"
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
					"patching_rect" : [ 30.0, 736.0, 76.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "phasor",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 108.0, 736.0, 78.0, 22.0 ],
					"text" : "phasor~ 110."
				}

			}
, 			{
				"box" : 				{
					"id" : "wave",
					"maxclass" : "newobj",
					"numinlets" : 3,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 212.0, 736.0, 184.0, 22.0 ],
					"text" : "wave~ qmw_full4q_setting"
				}

			}
, 			{
				"box" : 				{
					"id" : "gain",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 412.0, 736.0, 58.0, 22.0 ],
					"text" : "*~ 0.12"
				}

			}
, 			{
				"box" : 				{
					"id" : "dac",
					"maxclass" : "ezdac~",
					"numinlets" : 2,
					"numoutlets" : 0,
					"patching_rect" : [ 490.0, 728.0, 45.0, 45.0 ]
				}

			}
, 			{
				"box" : 				{
					"fontsize" : 11.0,
					"id" : "warning",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 30.0, 782.0, 520.0, 19.0 ],
					"text" : "SOURCE MEMORY · reload the latest saved datasets without rerunning either source."
				}

			}
, 			{
				"box" : 				{
					"id" : "replay_local",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 30.0, 810.0, 118.0, 22.0 ],
					"text" : "local"
				}

			}
, 			{
				"box" : 				{
					"id" : "replay_ibm",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 160.0, 810.0, 118.0, 22.0 ],
					"text" : "ibm"
				}

			}
, 			{
				"box" : 				{
					"id" : "opack_replay",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "FullPacket" ],
					"patching_rect" : [ 290.0, 810.0, 220.0, 22.0 ],
					"text" : "o.pack /qmw/tomography/replay"
				}

			}
, 			{
				"box" : 				{
					"fontsize" : 11.0,
					"id" : "replay_help",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 520.0, 810.0, 390.0, 19.0 ],
					"text" : "LOAD LAST LOCAL / LOAD LAST IBM"
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
					"patching_rect" : [ 30.0, 842.0, 86.0, 22.0 ],
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
					"patching_rect" : [ 130.0, 842.0, 78.0, 22.0 ],
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
					"patching_rect" : [ 220.0, 842.0, 78.0, 22.0 ],
					"text" : "loadmess 0."
				}

			}
, 			{
				"box" : 				{
					"id" : "receiver",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 5,
					"outlettype" : [ "", "", "", "", "" ],
					"patching_rect" : [ 1160.0, 688.0, 232.0, 22.0 ],
					"saved_object_attributes" : 					{
						"filename" : "qmw_full4q_tomography_receiver_v1.js",
						"parameter_enable" : 0
					}
,
					"text" : "js qmw_full4q_tomography_receiver_v1.js"
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
					"patching_rect" : [ 30.0, 900.0, 140.0, 22.0 ],
					"text" : "udpreceive 7426"
				}

			}
, 			{
				"box" : 				{
					"hidden" : 1,
					"id" : "route",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 11,
					"outlettype" : [ "", "", "", "", "", "", "", "", "", "", "FullPacket" ],
					"patching_rect" : [ 184.0, 900.0, 1358.0, 22.0 ],
					"text" : "o.route /qmw/tomography/begin /qmw/tomography/setting /qmw/tomography/pauli /qmw/tomography/shell /qmw/tomography/metrics /qmw/tomography/end /qmw/tomography/status /qmw/tomography/error /qmw/tomography/xfade /qmw/tomography/select"
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
					"patching_rect" : [ 184.0, 938.0, 100.0, 22.0 ],
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
					"patching_rect" : [ 294.0, 938.0, 100.0, 22.0 ],
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
					"patching_rect" : [ 404.0, 938.0, 100.0, 22.0 ],
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
					"patching_rect" : [ 514.0, 938.0, 100.0, 22.0 ],
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
					"patching_rect" : [ 624.0, 938.0, 100.0, 22.0 ],
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
					"patching_rect" : [ 734.0, 938.0, 100.0, 22.0 ],
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
					"patching_rect" : [ 844.0, 938.0, 100.0, 22.0 ],
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
					"patching_rect" : [ 954.0, 938.0, 100.0, 22.0 ],
					"text" : "prepend error"
				}

			}
 ],
		"lines" : [ 			{
				"patchline" : 				{
					"destination" : [ "opack_run", 0 ],
					"source" : [ "bell", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "phasor", 0 ],
					"hidden" : 1,
					"order" : 0,
					"source" : [ "frequency", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "warning", 0 ],
					"hidden" : 1,
					"order" : 1,
					"source" : [ "frequency", 0 ]
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
					"destination" : [ "opack_run", 0 ],
					"source" : [ "ghz", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "opack_run", 0 ],
					"source" : [ "ghzqft", 0 ]
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
					"destination" : [ "prepend_xfade", 0 ],
					"source" : [ "mix", 0 ]
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
					"hidden" : 1,
					"source" : [ "opack_replay", 0 ]
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
					"destination" : [ "wave", 0 ],
					"source" : [ "phasor", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "opack_ping", 0 ],
					"source" : [ "pingbutton", 0 ]
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
					"destination" : [ "receiver", 0 ],
					"source" : [ "prepend_xfade", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "heatmap", 0 ],
					"source" : [ "receiver", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "histogram", 0 ],
					"source" : [ "receiver", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "paulis", 0 ],
					"source" : [ "receiver", 2 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "shells", 0 ],
					"source" : [ "receiver", 3 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "status", 0 ],
					"source" : [ "receiver", 4 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "opack_replay", 0 ],
					"source" : [ "replay_ibm", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "opack_replay", 0 ],
					"source" : [ "replay_local", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "mix", 0 ],
					"hidden" : 1,
					"source" : [ "route", 8 ]
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
					"destination" : [ "select", 0 ],
					"hidden" : 1,
					"source" : [ "route", 9 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "prepend_select", 0 ],
					"source" : [ "select", 0 ]
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
					"destination" : [ "gain", 0 ],
					"source" : [ "wave", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "opack_run", 0 ],
					"source" : [ "weave", 0 ]
				}

			}
 ],
		"originid" : "pat-1009",
		"dependency_cache" : [ 			{
				"name" : "o.pack.mxo",
				"type" : "iLaX"
			}
, 			{
				"name" : "o.route.mxo",
				"type" : "iLaX"
			}
, 			{
				"name" : "qmw_full4q_tomography_receiver_v1.js",
				"bootpath" : "~/QuantumSonification/max",
				"patcherrelativepath" : ".",
				"type" : "TEXT",
				"implicit" : 1
			}
 ],
		"autosave" : 0
	}

}
