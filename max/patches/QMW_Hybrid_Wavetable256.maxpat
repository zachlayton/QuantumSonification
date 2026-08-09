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
		"rect" : [ 245.0, 213.0, 1120.0, 640.0 ],
		"gridsize" : [ 15.0, 15.0 ],
		"boxes" : [ 			{
				"box" : 				{
					"id" : "obj-title",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 35.0, 20.0, 510.0, 20.0 ],
					"text" : "QMW Hybrid Wavetable 256 — local render, double buffer, Gen~ crossfade"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-help",
					"linecount" : 3,
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 35.0, 47.0, 700.0, 47.0 ],
					"text" : "Inlets 1–5 accept the existing 16-value real / imag / magnitude / phase / speed lists.\nInlet 6 accepts oscillator frequency as a signal or float. Renderer output never returns to OSC.\nMessages such as weights 0.58 0.27 0.15 and smoothing 0.35 may also enter inlet 1."
				}

			}
, 			{
				"box" : 				{
					"comment" : "real list",
					"id" : "obj-in-real",
					"index" : 1,
					"maxclass" : "inlet",
					"numinlets" : 0,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 45.0, 125.0, 30.0, 30.0 ]
				}

			}
, 			{
				"box" : 				{
					"comment" : "imag list",
					"id" : "obj-in-imag",
					"index" : 2,
					"maxclass" : "inlet",
					"numinlets" : 0,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 145.0, 125.0, 30.0, 30.0 ]
				}

			}
, 			{
				"box" : 				{
					"comment" : "magnitude list",
					"id" : "obj-in-mag",
					"index" : 3,
					"maxclass" : "inlet",
					"numinlets" : 0,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 245.0, 125.0, 30.0, 30.0 ]
				}

			}
, 			{
				"box" : 				{
					"comment" : "phase list",
					"id" : "obj-in-phase",
					"index" : 4,
					"maxclass" : "inlet",
					"numinlets" : 0,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 345.0, 125.0, 30.0, 30.0 ]
				}

			}
, 			{
				"box" : 				{
					"comment" : "speed list",
					"id" : "obj-in-speed",
					"index" : 5,
					"maxclass" : "inlet",
					"numinlets" : 0,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 445.0, 125.0, 30.0, 30.0 ]
				}

			}
, 			{
				"box" : 				{
					"comment" : "frequency",
					"id" : "obj-in-freq",
					"index" : 6,
					"maxclass" : "inlet",
					"numinlets" : 0,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 760.0, 125.0, 30.0, 30.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-js",
					"maxclass" : "newobj",
					"numinlets" : 5,
					"numoutlets" : 2,
					"outlettype" : [ "", "" ],
					"patching_rect" : [ 45.0, 205.0, 430.0, 22.0 ],
					"saved_object_attributes" : 					{
						"filename" : "qmw_hybrid_wavetable_renderer.js",
						"parameter_enable" : 0
					}
,
					"text" : "js qmw_hybrid_wavetable_renderer.js"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-buffer-a",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "float", "bang" ],
					"patching_rect" : [ 45.0, 270.0, 310.0, 22.0 ],
					"text" : "buffer~ qmw_hybrid_table_A @samps 256 @channels 1"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-buffer-b",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "float", "bang" ],
					"patching_rect" : [ 375.0, 270.0, 310.0, 22.0 ],
					"text" : "buffer~ qmw_hybrid_table_B @samps 256 @channels 1"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-sig",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 760.0, 205.0, 52.0, 22.0 ],
					"text" : "sig~ 55"
				}

			}
, 			{
				"box" : 				{
					"code" : "// QMW hybrid double-buffer wavetable voice.\nBuffer table_a(\"qmw_hybrid_table_A\");\nBuffer table_b(\"qmw_hybrid_table_B\");\nParam amp(0.2);\nParam default_freq(55);\nParam table_mix(0);\nParam crossfade_ms(50);\nHistory phase(0);\nHistory smooth_mix(0);\nfreq = (in1 > 0) * in1 + (in1 <= 0) * default_freq;\nphase = fract(phase + freq / samplerate);\nfade_ms = max(crossfade_ms, 0.5);\nfade_coeff = exp(-1 / (fade_ms * 0.0001 * samplerate));\nsmooth_mix = table_mix + fade_coeff * (smooth_mix - table_mix);\nsample_a, index_a = wave(table_a, phase, 0, 256, 0, channels=1);\nsample_b, index_b = wave(table_b, phase, 0, 256, 0, channels=1);\nsample = mix(sample_a, sample_b, smooth_mix);\nout1 = sample * amp;\nout2 = phase;\nout3 = smooth_mix;\n",
					"fontface" : 0,
					"fontname" : "<Monospaced>",
					"fontsize" : 12.0,
					"id" : "obj-gen",
					"maxclass" : "gen.codebox~",
					"numinlets" : 1,
					"numoutlets" : 3,
					"outlettype" : [ "signal", "signal", "signal" ],
					"patching_rect" : [ 625.0, 335.0, 385.0, 215.0 ]
				}

			}
, 			{
				"box" : 				{
					"comment" : "audio",
					"id" : "obj-out-audio",
					"index" : 2,
					"maxclass" : "outlet",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 625.0, 585.0, 30.0, 30.0 ]
				}

			}
, 			{
				"box" : 				{
					"comment" : "render status",
					"id" : "obj-out-status",
					"index" : 1,
					"maxclass" : "outlet",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 475.0, 585.0, 30.0, 30.0 ]
				}

			}
, 			{
				"box" : 				{
					"buffername" : "qmw_hybrid_table_A",
					"id" : "obj-wave-a",
					"maxclass" : "waveform~",
					"numinlets" : 5,
					"numoutlets" : 6,
					"outlettype" : [ "float", "float", "float", "float", "list", "" ],
					"patching_rect" : [ 45.0, 320.0, 250.0, 115.0 ]
				}

			}
, 			{
				"box" : 				{
					"buffername" : "qmw_hybrid_table_B",
					"id" : "obj-wave-b",
					"maxclass" : "waveform~",
					"numinlets" : 5,
					"numoutlets" : 6,
					"outlettype" : [ "float", "float", "float", "float", "list", "" ],
					"patching_rect" : [ 320.0, 320.0, 250.0, 115.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-load",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "bang" ],
					"patching_rect" : [ 45.0, 475.0, 60.0, 22.0 ],
					"text" : "loadbang"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-init",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 120.0, 475.0, 251.0, 22.0 ],
					"text" : "weights 0.58 0.27 0.15, smoothing 0.95, bang"
				}

			}
 ],
		"lines" : [ 			{
				"patchline" : 				{
					"destination" : [ "obj-out-audio", 0 ],
					"source" : [ "obj-gen", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-sig", 0 ],
					"source" : [ "obj-in-freq", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-js", 1 ],
					"source" : [ "obj-in-imag", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-js", 2 ],
					"source" : [ "obj-in-mag", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-js", 3 ],
					"source" : [ "obj-in-phase", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-js", 0 ],
					"source" : [ "obj-in-real", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-js", 4 ],
					"source" : [ "obj-in-speed", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-js", 0 ],
					"source" : [ "obj-init", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-gen", 0 ],
					"source" : [ "obj-js", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-out-status", 0 ],
					"source" : [ "obj-js", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-init", 0 ],
					"source" : [ "obj-load", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-gen", 0 ],
					"source" : [ "obj-sig", 0 ]
				}

			}
 ],
		"originid" : "pat-8"
	}

}
