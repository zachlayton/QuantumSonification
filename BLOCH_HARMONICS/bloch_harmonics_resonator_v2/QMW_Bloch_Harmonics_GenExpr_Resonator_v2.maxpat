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
		"rect" : [ 34.0, 100.0, 1444.0, 816.0 ],
		"openinpresentation" : 1,
		"gridsize" : [ 15.0, 15.0 ],
		"boxes" : [ 			{
				"box" : 				{
					"fontsize" : 18.0,
					"id" : "obj-1",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 20.0, 15.0, 690.0, 27.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 20.0, 15.0, 720.0, 27.0 ],
					"text" : "BLOCH SPHERE → GENEXPR RESONATOR v2"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-2",
					"linecount" : 2,
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 20.0, 43.0, 732.0, 33.0 ],
					"presentation" : 1,
					"presentation_linecount" : 2,
					"presentation_rect" : [ 20.0, 43.0, 730.0, 33.0 ],
					"text" : "Move θ and φ in the visualization. Signed Yℓm values excite the canonical 16-lane GenExpr resonator: magnitude drives excitation, sign drives phase, and one fundamental transposes the complete field."
				}

			}
, 			{
				"box" : 				{
					"disablefind" : 0,
					"id" : "obj-3",
					"maxclass" : "jweb",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 20.0, 90.0, 740.0, 720.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 20.0, 90.0, 740.0, 720.0 ],
					"rendermode" : 0,
					"url" : "file://bloch-harmonics-max-direct.html"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-4",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "bang" ],
					"patching_rect" : [ 800.0, 720.0, 60.0, 22.0 ],
					"text" : "loadbang"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-5",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 800.0, 750.0, 225.0, 22.0 ],
					"text" : "readfile bloch-harmonics-max-direct.html"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-6",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 2,
					"outlettype" : [ "", "" ],
					"patching_rect" : [ 800.0, 90.0, 120.0, 22.0 ],
					"text" : "route maxmessage"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-7",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 2,
					"outlettype" : [ "", "" ],
					"patching_rect" : [ 800.0, 120.0, 80.0, 22.0 ],
					"text" : "route state"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-8",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 20,
					"outlettype" : [ "float", "float", "float", "float", "float", "float", "float", "float", "float", "float", "float", "float", "float", "float", "float", "float", "float", "float", "float", "float" ],
					"patching_rect" : [ 800.0, 150.0, 570.0, 22.0 ],
					"text" : "unpack f f f f f f f f f f f f f f f f f f f f"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-9",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 790.0, 205.0, 100.0, 20.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 790.0, 110.0, 110.0, 20.0 ],
					"text" : "θ (degrees)"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "obj-10",
					"maxclass" : "flonum",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 900.0, 200.0, 95.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 900.0, 105.0, 95.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-11",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 790.0, 259.0, 100.0, 20.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 790.0, 164.0, 110.0, 20.0 ],
					"text" : "φ (degrees)"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "obj-12",
					"maxclass" : "flonum",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 900.0, 254.0, 95.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 900.0, 159.0, 95.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-13",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 790.0, 313.0, 100.0, 20.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 790.0, 218.0, 110.0, 20.0 ],
					"text" : "Bloch X"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "obj-14",
					"maxclass" : "flonum",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 900.0, 308.0, 95.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 900.0, 213.0, 95.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-15",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 790.0, 367.0, 100.0, 20.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 790.0, 272.0, 110.0, 20.0 ],
					"text" : "Bloch Y"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "obj-16",
					"maxclass" : "flonum",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 900.0, 362.0, 95.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 900.0, 267.0, 95.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-17",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 790.0, 421.0, 100.0, 20.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 790.0, 326.0, 110.0, 20.0 ],
					"text" : "Bloch Z"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "obj-18",
					"maxclass" : "flonum",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 900.0, 416.0, 95.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 900.0, 321.0, 95.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"fontsize" : 14.0,
					"id" : "obj-19",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 790.0, 175.0, 260.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 790.0, 80.0, 280.0, 22.0 ],
					"text" : "Live state from the animation"
				}

			}
, 			{
				"box" : 				{
					"fontsize" : 14.0,
					"id" : "obj-120",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 790.0, 640.0, 220.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 790.0, 625.0, 240.0, 22.0 ],
					"text" : "GenExpr resonator mapping"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-121",
					"linecount" : 2,
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 790.0, 670.0, 583.0, 33.0 ],
					"presentation" : 1,
					"presentation_linecount" : 2,
					"presentation_rect" : [ 790.0, 655.0, 580.0, 33.0 ],
					"text" : "|Yℓm| → resonator magnitude  •  sign(Yℓm) → 0/π phase  •  degree sets decay speed\\nThe first 15 resonant lanes follow the visible bars; lane 16 remains reserved."
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-122",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 790.0, 730.0, 500.0, 20.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 790.0, 715.0, 520.0, 20.0 ],
					"text" : "Runtime asset: bloch-harmonics-max-direct.html must remain beside this patch.",
					"textcolor" : [ 0.45, 0.45, 0.45, 1.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-123",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 2,
					"outlettype" : [ "", "" ],
					"patching_rect" : [ 940.0, 90.0, 75.0, 22.0 ],
					"text" : "route state"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-124",
					"maxclass" : "button",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 1030.0, 90.0, 24.0, 24.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 1030.0, 80.0, 24.0, 24.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-125",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 1060.0, 92.0, 160.0, 20.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 1060.0, 82.0, 180.0, 20.0 ],
					"text" : "harmonic bridge activity"
				}

			}
, 			{
				"box" : 				{
					"code" : "// QMW Density Field Quantum Resonator 16\n//\n// Gen~ codebox.\n// in1 is the carrier frequency in Hz.\n// m0..m15 excite sixteen resonant partials.\n// ph0..ph15 set smoothed per-partial timing/phase.\n// s0..s15 set lifetime: fast lanes flash, slow lanes ring.\n// h0..h15 are partial ratios. Defaults are harmonic 1..16, but these can\n// later be replaced by Hamiltonian energy-gap ratios.\n\nParam m0(0);\nParam m1(0);\nParam m2(0);\nParam m3(0);\nParam m4(0);\nParam m5(0);\nParam m6(0);\nParam m7(0);\nParam m8(0);\nParam m9(0);\nParam m10(0);\nParam m11(0);\nParam m12(0);\nParam m13(0);\nParam m14(0);\nParam m15(0);\n\nParam ph0(0);\nParam ph1(0);\nParam ph2(0);\nParam ph3(0);\nParam ph4(0);\nParam ph5(0);\nParam ph6(0);\nParam ph7(0);\nParam ph8(0);\nParam ph9(0);\nParam ph10(0);\nParam ph11(0);\nParam ph12(0);\nParam ph13(0);\nParam ph14(0);\nParam ph15(0);\n\nParam s0(0);\nParam s1(0);\nParam s2(0);\nParam s3(0);\nParam s4(0);\nParam s5(0);\nParam s6(0);\nParam s7(0);\nParam s8(0);\nParam s9(0);\nParam s10(0);\nParam s11(0);\nParam s12(0);\nParam s13(0);\nParam s14(0);\nParam s15(0);\n\nParam h0(1);\nParam h1(2);\nParam h2(3);\nParam h3(4);\nParam h4(5);\nParam h5(6);\nParam h6(7);\nParam h7(8);\nParam h8(9);\nParam h9(10);\nParam h10(11);\nParam h11(12);\nParam h12(13);\nParam h13(14);\nParam h14(15);\nParam h15(16);\n\nParam purity(1);\nParam entropy(0);\nParam coherence(0);\nParam amp(0.2);\nParam default_freq(55);\nParam attack_ms(12);\nParam slow_decay_ms(900);\nParam fast_decay_ms(70);\nParam phase_smooth_ms(100);\nParam magnitude_smooth_ms(100);\nParam brightness(0.65);\nParam mix_voices(4);\nParam output_ceiling(0.85);\n\nHistory p0(0);\nHistory p1(0);\nHistory p2(0);\nHistory p3(0);\nHistory p4(0);\nHistory p5(0);\nHistory p6(0);\nHistory p7(0);\nHistory p8(0);\nHistory p9(0);\nHistory p10(0);\nHistory p11(0);\nHistory p12(0);\nHistory p13(0);\nHistory p14(0);\nHistory p15(0);\n\nHistory e0(0);\nHistory e1(0);\nHistory e2(0);\nHistory e3(0);\nHistory e4(0);\nHistory e5(0);\nHistory e6(0);\nHistory e7(0);\nHistory e8(0);\nHistory e9(0);\nHistory e10(0);\nHistory e11(0);\nHistory e12(0);\nHistory e13(0);\nHistory e14(0);\nHistory e15(0);\n\nHistory sm0(0);\nHistory sm1(0);\nHistory sm2(0);\nHistory sm3(0);\nHistory sm4(0);\nHistory sm5(0);\nHistory sm6(0);\nHistory sm7(0);\nHistory sm8(0);\nHistory sm9(0);\nHistory sm10(0);\nHistory sm11(0);\nHistory sm12(0);\nHistory sm13(0);\nHistory sm14(0);\nHistory sm15(0);\n\nHistory sph0(0);\nHistory sph1(0);\nHistory sph2(0);\nHistory sph3(0);\nHistory sph4(0);\nHistory sph5(0);\nHistory sph6(0);\nHistory sph7(0);\nHistory sph8(0);\nHistory sph9(0);\nHistory sph10(0);\nHistory sph11(0);\nHistory sph12(0);\nHistory sph13(0);\nHistory sph14(0);\nHistory sph15(0);\n\nfreq = (in1 > 0) * in1 + (in1 <= 0) * default_freq;\npur = clamp(purity, 0, 1);\nent = clamp(entropy, 0, 1);\ncoh = clamp(coherence, 0, 1);\n\nmag_ms = max(magnitude_smooth_ms, 0.1);\nmag_coeff = exp(-1 / (mag_ms * 0.001 * samplerate));\n\ntm0 = clamp(m0, 0, 1);\ntm1 = clamp(m1, 0, 1);\ntm2 = clamp(m2, 0, 1);\ntm3 = clamp(m3, 0, 1);\ntm4 = clamp(m4, 0, 1);\ntm5 = clamp(m5, 0, 1);\ntm6 = clamp(m6, 0, 1);\ntm7 = clamp(m7, 0, 1);\ntm8 = clamp(m8, 0, 1);\ntm9 = clamp(m9, 0, 1);\ntm10 = clamp(m10, 0, 1);\ntm11 = clamp(m11, 0, 1);\ntm12 = clamp(m12, 0, 1);\ntm13 = clamp(m13, 0, 1);\ntm14 = clamp(m14, 0, 1);\ntm15 = clamp(m15, 0, 1);\n\nsm0 = tm0 + mag_coeff * (sm0 - tm0);\nsm1 = tm1 + mag_coeff * (sm1 - tm1);\nsm2 = tm2 + mag_coeff * (sm2 - tm2);\nsm3 = tm3 + mag_coeff * (sm3 - tm3);\nsm4 = tm4 + mag_coeff * (sm4 - tm4);\nsm5 = tm5 + mag_coeff * (sm5 - tm5);\nsm6 = tm6 + mag_coeff * (sm6 - tm6);\nsm7 = tm7 + mag_coeff * (sm7 - tm7);\nsm8 = tm8 + mag_coeff * (sm8 - tm8);\nsm9 = tm9 + mag_coeff * (sm9 - tm9);\nsm10 = tm10 + mag_coeff * (sm10 - tm10);\nsm11 = tm11 + mag_coeff * (sm11 - tm11);\nsm12 = tm12 + mag_coeff * (sm12 - tm12);\nsm13 = tm13 + mag_coeff * (sm13 - tm13);\nsm14 = tm14 + mag_coeff * (sm14 - tm14);\nsm15 = tm15 + mag_coeff * (sm15 - tm15);\n\nphase_ms = max(phase_smooth_ms, 0.1);\nphase_coeff = exp(-1 / (phase_ms * 0.001 * samplerate));\n\ndph0 = atan2(sin(ph0 - sph0), cos(ph0 - sph0));\ndph1 = atan2(sin(ph1 - sph1), cos(ph1 - sph1));\ndph2 = atan2(sin(ph2 - sph2), cos(ph2 - sph2));\ndph3 = atan2(sin(ph3 - sph3), cos(ph3 - sph3));\ndph4 = atan2(sin(ph4 - sph4), cos(ph4 - sph4));\ndph5 = atan2(sin(ph5 - sph5), cos(ph5 - sph5));\ndph6 = atan2(sin(ph6 - sph6), cos(ph6 - sph6));\ndph7 = atan2(sin(ph7 - sph7), cos(ph7 - sph7));\ndph8 = atan2(sin(ph8 - sph8), cos(ph8 - sph8));\ndph9 = atan2(sin(ph9 - sph9), cos(ph9 - sph9));\ndph10 = atan2(sin(ph10 - sph10), cos(ph10 - sph10));\ndph11 = atan2(sin(ph11 - sph11), cos(ph11 - sph11));\ndph12 = atan2(sin(ph12 - sph12), cos(ph12 - sph12));\ndph13 = atan2(sin(ph13 - sph13), cos(ph13 - sph13));\ndph14 = atan2(sin(ph14 - sph14), cos(ph14 - sph14));\ndph15 = atan2(sin(ph15 - sph15), cos(ph15 - sph15));\n\nsph0 = sph0 + (1 - phase_coeff) * dph0;\nsph1 = sph1 + (1 - phase_coeff) * dph1;\nsph2 = sph2 + (1 - phase_coeff) * dph2;\nsph3 = sph3 + (1 - phase_coeff) * dph3;\nsph4 = sph4 + (1 - phase_coeff) * dph4;\nsph5 = sph5 + (1 - phase_coeff) * dph5;\nsph6 = sph6 + (1 - phase_coeff) * dph6;\nsph7 = sph7 + (1 - phase_coeff) * dph7;\nsph8 = sph8 + (1 - phase_coeff) * dph8;\nsph9 = sph9 + (1 - phase_coeff) * dph9;\nsph10 = sph10 + (1 - phase_coeff) * dph10;\nsph11 = sph11 + (1 - phase_coeff) * dph11;\nsph12 = sph12 + (1 - phase_coeff) * dph12;\nsph13 = sph13 + (1 - phase_coeff) * dph13;\nsph14 = sph14 + (1 - phase_coeff) * dph14;\nsph15 = sph15 + (1 - phase_coeff) * dph15;\n\natk_ms = max(attack_ms * mix(1.35, 0.65, coh), 0.1);\natk_coeff = exp(-1 / (atk_ms * 0.001 * samplerate));\n\nspd0 = clamp(abs(s0), 0, 1);\nspd1 = clamp(abs(s1), 0, 1);\nspd2 = clamp(abs(s2), 0, 1);\nspd3 = clamp(abs(s3), 0, 1);\nspd4 = clamp(abs(s4), 0, 1);\nspd5 = clamp(abs(s5), 0, 1);\nspd6 = clamp(abs(s6), 0, 1);\nspd7 = clamp(abs(s7), 0, 1);\nspd8 = clamp(abs(s8), 0, 1);\nspd9 = clamp(abs(s9), 0, 1);\nspd10 = clamp(abs(s10), 0, 1);\nspd11 = clamp(abs(s11), 0, 1);\nspd12 = clamp(abs(s12), 0, 1);\nspd13 = clamp(abs(s13), 0, 1);\nspd14 = clamp(abs(s14), 0, 1);\nspd15 = clamp(abs(s15), 0, 1);\n\ndec0 = mix(slow_decay_ms, fast_decay_ms, spd0);\ndec1 = mix(slow_decay_ms, fast_decay_ms, spd1);\ndec2 = mix(slow_decay_ms, fast_decay_ms, spd2);\ndec3 = mix(slow_decay_ms, fast_decay_ms, spd3);\ndec4 = mix(slow_decay_ms, fast_decay_ms, spd4);\ndec5 = mix(slow_decay_ms, fast_decay_ms, spd5);\ndec6 = mix(slow_decay_ms, fast_decay_ms, spd6);\ndec7 = mix(slow_decay_ms, fast_decay_ms, spd7);\ndec8 = mix(slow_decay_ms, fast_decay_ms, spd8);\ndec9 = mix(slow_decay_ms, fast_decay_ms, spd9);\ndec10 = mix(slow_decay_ms, fast_decay_ms, spd10);\ndec11 = mix(slow_decay_ms, fast_decay_ms, spd11);\ndec12 = mix(slow_decay_ms, fast_decay_ms, spd12);\ndec13 = mix(slow_decay_ms, fast_decay_ms, spd13);\ndec14 = mix(slow_decay_ms, fast_decay_ms, spd14);\ndec15 = mix(slow_decay_ms, fast_decay_ms, spd15);\n\ndc0 = exp(-1 / (max(dec0, 0.1) * 0.001 * samplerate));\ndc1 = exp(-1 / (max(dec1, 0.1) * 0.001 * samplerate));\ndc2 = exp(-1 / (max(dec2, 0.1) * 0.001 * samplerate));\ndc3 = exp(-1 / (max(dec3, 0.1) * 0.001 * samplerate));\ndc4 = exp(-1 / (max(dec4, 0.1) * 0.001 * samplerate));\ndc5 = exp(-1 / (max(dec5, 0.1) * 0.001 * samplerate));\ndc6 = exp(-1 / (max(dec6, 0.1) * 0.001 * samplerate));\ndc7 = exp(-1 / (max(dec7, 0.1) * 0.001 * samplerate));\ndc8 = exp(-1 / (max(dec8, 0.1) * 0.001 * samplerate));\ndc9 = exp(-1 / (max(dec9, 0.1) * 0.001 * samplerate));\ndc10 = exp(-1 / (max(dec10, 0.1) * 0.001 * samplerate));\ndc11 = exp(-1 / (max(dec11, 0.1) * 0.001 * samplerate));\ndc12 = exp(-1 / (max(dec12, 0.1) * 0.001 * samplerate));\ndc13 = exp(-1 / (max(dec13, 0.1) * 0.001 * samplerate));\ndc14 = exp(-1 / (max(dec14, 0.1) * 0.001 * samplerate));\ndc15 = exp(-1 / (max(dec15, 0.1) * 0.001 * samplerate));\n\n// Higher entropy lifts weaker modes. Higher purity makes excitation more selective.\nexc_shape = mix(0.55, 1.6, pur);\nt0 = pow(sm0 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt1 = pow(sm1 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt2 = pow(sm2 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt3 = pow(sm3 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt4 = pow(sm4 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt5 = pow(sm5 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt6 = pow(sm6 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt7 = pow(sm7 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt8 = pow(sm8 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt9 = pow(sm9 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt10 = pow(sm10 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt11 = pow(sm11 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt12 = pow(sm12 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt13 = pow(sm13 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt14 = pow(sm14 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt15 = pow(sm15 + 0.00001, exc_shape) * mix(0.35, 1, ent);\n\ne0 = (t0 > e0) * (t0 + atk_coeff * (e0 - t0)) + (t0 <= e0) * (t0 + dc0 * (e0 - t0));\ne1 = (t1 > e1) * (t1 + atk_coeff * (e1 - t1)) + (t1 <= e1) * (t1 + dc1 * (e1 - t1));\ne2 = (t2 > e2) * (t2 + atk_coeff * (e2 - t2)) + (t2 <= e2) * (t2 + dc2 * (e2 - t2));\ne3 = (t3 > e3) * (t3 + atk_coeff * (e3 - t3)) + (t3 <= e3) * (t3 + dc3 * (e3 - t3));\ne4 = (t4 > e4) * (t4 + atk_coeff * (e4 - t4)) + (t4 <= e4) * (t4 + dc4 * (e4 - t4));\ne5 = (t5 > e5) * (t5 + atk_coeff * (e5 - t5)) + (t5 <= e5) * (t5 + dc5 * (e5 - t5));\ne6 = (t6 > e6) * (t6 + atk_coeff * (e6 - t6)) + (t6 <= e6) * (t6 + dc6 * (e6 - t6));\ne7 = (t7 > e7) * (t7 + atk_coeff * (e7 - t7)) + (t7 <= e7) * (t7 + dc7 * (e7 - t7));\ne8 = (t8 > e8) * (t8 + atk_coeff * (e8 - t8)) + (t8 <= e8) * (t8 + dc8 * (e8 - t8));\ne9 = (t9 > e9) * (t9 + atk_coeff * (e9 - t9)) + (t9 <= e9) * (t9 + dc9 * (e9 - t9));\ne10 = (t10 > e10) * (t10 + atk_coeff * (e10 - t10)) + (t10 <= e10) * (t10 + dc10 * (e10 - t10));\ne11 = (t11 > e11) * (t11 + atk_coeff * (e11 - t11)) + (t11 <= e11) * (t11 + dc11 * (e11 - t11));\ne12 = (t12 > e12) * (t12 + atk_coeff * (e12 - t12)) + (t12 <= e12) * (t12 + dc12 * (e12 - t12));\ne13 = (t13 > e13) * (t13 + atk_coeff * (e13 - t13)) + (t13 <= e13) * (t13 + dc13 * (e13 - t13));\ne14 = (t14 > e14) * (t14 + atk_coeff * (e14 - t14)) + (t14 <= e14) * (t14 + dc14 * (e14 - t14));\ne15 = (t15 > e15) * (t15 + atk_coeff * (e15 - t15)) + (t15 <= e15) * (t15 + dc15 * (e15 - t15));\n\nbright = clamp(brightness + ent * 0.25, 0, 1);\n\np0 = fract(p0 + freq * max(h0, 0.01) / samplerate);\np1 = fract(p1 + freq * max(h1, 0.01) / samplerate);\np2 = fract(p2 + freq * max(h2, 0.01) / samplerate);\np3 = fract(p3 + freq * max(h3, 0.01) / samplerate);\np4 = fract(p4 + freq * max(h4, 0.01) / samplerate);\np5 = fract(p5 + freq * max(h5, 0.01) / samplerate);\np6 = fract(p6 + freq * max(h6, 0.01) / samplerate);\np7 = fract(p7 + freq * max(h7, 0.01) / samplerate);\np8 = fract(p8 + freq * max(h8, 0.01) / samplerate);\np9 = fract(p9 + freq * max(h9, 0.01) / samplerate);\np10 = fract(p10 + freq * max(h10, 0.01) / samplerate);\np11 = fract(p11 + freq * max(h11, 0.01) / samplerate);\np12 = fract(p12 + freq * max(h12, 0.01) / samplerate);\np13 = fract(p13 + freq * max(h13, 0.01) / samplerate);\np14 = fract(p14 + freq * max(h14, 0.01) / samplerate);\np15 = fract(p15 + freq * max(h15, 0.01) / samplerate);\n\ntwopi = 6.283185307179586;\npartials =\n    e0 * sin(twopi * p0 + sph0) / pow(max(h0, 1), bright) +\n    e1 * sin(twopi * p1 + sph1) / pow(max(h1, 1), bright) +\n    e2 * sin(twopi * p2 + sph2) / pow(max(h2, 1), bright) +\n    e3 * sin(twopi * p3 + sph3) / pow(max(h3, 1), bright) +\n    e4 * sin(twopi * p4 + sph4) / pow(max(h4, 1), bright) +\n    e5 * sin(twopi * p5 + sph5) / pow(max(h5, 1), bright) +\n    e6 * sin(twopi * p6 + sph6) / pow(max(h6, 1), bright) +\n    e7 * sin(twopi * p7 + sph7) / pow(max(h7, 1), bright) +\n    e8 * sin(twopi * p8 + sph8) / pow(max(h8, 1), bright) +\n    e9 * sin(twopi * p9 + sph9) / pow(max(h9, 1), bright) +\n    e10 * sin(twopi * p10 + sph10) / pow(max(h10, 1), bright) +\n    e11 * sin(twopi * p11 + sph11) / pow(max(h11, 1), bright) +\n    e12 * sin(twopi * p12 + sph12) / pow(max(h12, 1), bright) +\n    e13 * sin(twopi * p13 + sph13) / pow(max(h13, 1), bright) +\n    e14 * sin(twopi * p14 + sph14) / pow(max(h14, 1), bright) +\n    e15 * sin(twopi * p15 + sph15) / pow(max(h15, 1), bright);\n\nvoice_scale = 1 / sqrt(max(mix_voices, 1));\nsig = tanh(partials * 0.5);\n\nout1 = sig * amp * output_ceiling * voice_scale;\nout2 = e0 + e1 + e2 + e3 + e4 + e5 + e6 + e7 + e8 + e9 + e10 + e11 + e12 + e13 + e14 + e15;\nout3 = freq;\n",
					"fontface" : 0,
					"fontname" : "<Monospaced>",
					"fontsize" : 12.0,
					"id" : "obj-200",
					"maxclass" : "gen.codebox~",
					"numinlets" : 1,
					"numoutlets" : 3,
					"outlettype" : [ "signal", "signal", "signal" ],
					"patching_rect" : [ 674.0, 862.0, 150.0, 60.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-201",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 790.0, 385.0, 110.0, 20.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 790.0, 375.0, 110.0, 20.0 ],
					"text" : "Fundamental (Hz)"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "obj-202",
					"maxclass" : "flonum",
					"maximum" : 1000.0,
					"minimum" : 20.0,
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 905.0, 380.0, 85.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 905.0, 370.0, 85.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-203",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1000.0, 380.0, 85.0, 22.0 ],
					"text" : "loadmess 55."
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-204",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 1095.0, 380.0, 38.0, 22.0 ],
					"text" : "sig~"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-205",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 790.0, 420.0, 110.0, 20.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 790.0, 410.0, 110.0, 20.0 ],
					"text" : "Brightness"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "obj-206",
					"maxclass" : "flonum",
					"maximum" : 1.0,
					"minimum" : 0.0,
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 905.0, 415.0, 85.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 905.0, 405.0, 85.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-207",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1000.0, 415.0, 140.0, 22.0 ],
					"text" : "prepend brightness"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-208",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1150.0, 415.0, 95.0, 22.0 ],
					"text" : "loadmess 0.65"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-209",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 790.0, 455.0, 110.0, 20.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 790.0, 445.0, 110.0, 20.0 ],
					"text" : "Purity"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "obj-210",
					"maxclass" : "flonum",
					"maximum" : 1.0,
					"minimum" : 0.0,
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 905.0, 450.0, 85.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 905.0, 440.0, 85.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-211",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1000.0, 450.0, 140.0, 22.0 ],
					"text" : "prepend purity"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-212",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1150.0, 450.0, 95.0, 22.0 ],
					"text" : "loadmess 1"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-213",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 790.0, 490.0, 110.0, 20.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 790.0, 480.0, 110.0, 20.0 ],
					"text" : "Entropy"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "obj-214",
					"maxclass" : "flonum",
					"maximum" : 1.0,
					"minimum" : 0.0,
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 905.0, 485.0, 85.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 905.0, 475.0, 85.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-215",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1000.0, 485.0, 140.0, 22.0 ],
					"text" : "prepend entropy"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-216",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1150.0, 485.0, 95.0, 22.0 ],
					"text" : "loadmess 0.12"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-217",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 790.0, 525.0, 110.0, 20.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 790.0, 515.0, 110.0, 20.0 ],
					"text" : "Coherence"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "obj-218",
					"maxclass" : "flonum",
					"maximum" : 1.0,
					"minimum" : 0.0,
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 905.0, 520.0, 85.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 905.0, 510.0, 85.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-219",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1000.0, 520.0, 140.0, 22.0 ],
					"text" : "prepend coherence"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-220",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1150.0, 520.0, 95.0, 22.0 ],
					"text" : "loadmess 0.7"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-221",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 790.0, 560.0, 110.0, 20.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 790.0, 550.0, 110.0, 20.0 ],
					"text" : "Slow decay (ms)"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "obj-222",
					"maxclass" : "flonum",
					"maximum" : 5000.0,
					"minimum" : 100.0,
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 905.0, 555.0, 85.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 905.0, 545.0, 85.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-223",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1000.0, 555.0, 141.0, 22.0 ],
					"text" : "prepend slow_decay_ms"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-224",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1150.0, 555.0, 95.0, 22.0 ],
					"text" : "loadmess 1200"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-225",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 790.0, 595.0, 110.0, 20.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 790.0, 585.0, 110.0, 20.0 ],
					"text" : "Fast decay (ms)"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "obj-226",
					"maxclass" : "flonum",
					"maximum" : 1000.0,
					"minimum" : 10.0,
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 905.0, 590.0, 85.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 905.0, 580.0, 85.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-227",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1000.0, 590.0, 140.0, 22.0 ],
					"text" : "prepend fast_decay_ms"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-228",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1150.0, 590.0, 95.0, 22.0 ],
					"text" : "loadmess 90"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-229",
					"linecount" : 2,
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 800.0, 800.0, 390.0, 35.0 ],
					"text" : "s0 0.18, s1 0.18, s2 0.18, s3 0.42, s4 0.42, s5 0.42, s6 0.42, s7 0.42, s8 0.72, s9 0.72, s10 0.72, s11 0.72, s12 0.72, s13 0.72, s14 0.72, s15 0.9"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-230",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "float" ],
					"patching_rect" : [ 800.0, 670.0, 48.0, 22.0 ],
					"text" : "abs 0."
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-231",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "float" ],
					"patching_rect" : [ 800.0, 697.0, 48.0, 22.0 ],
					"text" : "* 1.6"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-232",
					"maxclass" : "newobj",
					"numinlets" : 3,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 800.0, 724.0, 72.0, 22.0 ],
					"text" : "clip 0. 1."
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-233",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 800.0, 751.0, 82.0, 22.0 ],
					"text" : "prepend m0"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-234",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 886.0, 670.0, 155.0, 22.0 ],
					"text" : "expr ($f1 < 0.) * 3.141593"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-235",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 886.0, 697.0, 90.0, 22.0 ],
					"text" : "prepend ph0"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-236",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "float" ],
					"patching_rect" : [ 950.0, 670.0, 48.0, 22.0 ],
					"text" : "abs 0."
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-237",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "float" ],
					"patching_rect" : [ 950.0, 697.0, 48.0, 22.0 ],
					"text" : "* 1.6"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-238",
					"maxclass" : "newobj",
					"numinlets" : 3,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 950.0, 724.0, 72.0, 22.0 ],
					"text" : "clip 0. 1."
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-239",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 950.0, 751.0, 82.0, 22.0 ],
					"text" : "prepend m1"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-240",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1036.0, 670.0, 155.0, 22.0 ],
					"text" : "expr ($f1 < 0.) * 3.141593"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-241",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1036.0, 697.0, 90.0, 22.0 ],
					"text" : "prepend ph1"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-242",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "float" ],
					"patching_rect" : [ 1100.0, 670.0, 48.0, 22.0 ],
					"text" : "abs 0."
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-243",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "float" ],
					"patching_rect" : [ 1100.0, 697.0, 48.0, 22.0 ],
					"text" : "* 1.6"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-244",
					"maxclass" : "newobj",
					"numinlets" : 3,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1100.0, 724.0, 72.0, 22.0 ],
					"text" : "clip 0. 1."
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-245",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1100.0, 751.0, 82.0, 22.0 ],
					"text" : "prepend m2"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-246",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1186.0, 670.0, 155.0, 22.0 ],
					"text" : "expr ($f1 < 0.) * 3.141593"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-247",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1186.0, 697.0, 90.0, 22.0 ],
					"text" : "prepend ph2"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-248",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "float" ],
					"patching_rect" : [ 1250.0, 670.0, 48.0, 22.0 ],
					"text" : "abs 0."
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-249",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "float" ],
					"patching_rect" : [ 1250.0, 697.0, 48.0, 22.0 ],
					"text" : "* 1.6"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-250",
					"maxclass" : "newobj",
					"numinlets" : 3,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1250.0, 724.0, 72.0, 22.0 ],
					"text" : "clip 0. 1."
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-251",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1250.0, 751.0, 82.0, 22.0 ],
					"text" : "prepend m3"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-252",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1336.0, 670.0, 155.0, 22.0 ],
					"text" : "expr ($f1 < 0.) * 3.141593"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-253",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1336.0, 697.0, 90.0, 22.0 ],
					"text" : "prepend ph3"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-254",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "float" ],
					"patching_rect" : [ 1400.0, 670.0, 48.0, 22.0 ],
					"text" : "abs 0."
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-255",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "float" ],
					"patching_rect" : [ 1400.0, 697.0, 48.0, 22.0 ],
					"text" : "* 1.6"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-256",
					"maxclass" : "newobj",
					"numinlets" : 3,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1400.0, 724.0, 72.0, 22.0 ],
					"text" : "clip 0. 1."
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-257",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1400.0, 751.0, 82.0, 22.0 ],
					"text" : "prepend m4"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-258",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1486.0, 670.0, 155.0, 22.0 ],
					"text" : "expr ($f1 < 0.) * 3.141593"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-259",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1486.0, 697.0, 90.0, 22.0 ],
					"text" : "prepend ph4"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-260",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "float" ],
					"patching_rect" : [ 800.0, 800.0, 48.0, 22.0 ],
					"text" : "abs 0."
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-261",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "float" ],
					"patching_rect" : [ 800.0, 827.0, 48.0, 22.0 ],
					"text" : "* 1.6"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-262",
					"maxclass" : "newobj",
					"numinlets" : 3,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 800.0, 854.0, 72.0, 22.0 ],
					"text" : "clip 0. 1."
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-263",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 800.0, 881.0, 82.0, 22.0 ],
					"text" : "prepend m5"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-264",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 886.0, 800.0, 155.0, 22.0 ],
					"text" : "expr ($f1 < 0.) * 3.141593"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-265",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 886.0, 827.0, 90.0, 22.0 ],
					"text" : "prepend ph5"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-266",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "float" ],
					"patching_rect" : [ 950.0, 800.0, 48.0, 22.0 ],
					"text" : "abs 0."
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-267",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "float" ],
					"patching_rect" : [ 950.0, 827.0, 48.0, 22.0 ],
					"text" : "* 1.6"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-268",
					"maxclass" : "newobj",
					"numinlets" : 3,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 950.0, 854.0, 72.0, 22.0 ],
					"text" : "clip 0. 1."
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-269",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 950.0, 881.0, 82.0, 22.0 ],
					"text" : "prepend m6"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-270",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1036.0, 800.0, 155.0, 22.0 ],
					"text" : "expr ($f1 < 0.) * 3.141593"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-271",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1036.0, 827.0, 90.0, 22.0 ],
					"text" : "prepend ph6"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-272",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "float" ],
					"patching_rect" : [ 1100.0, 800.0, 48.0, 22.0 ],
					"text" : "abs 0."
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-273",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "float" ],
					"patching_rect" : [ 1100.0, 827.0, 48.0, 22.0 ],
					"text" : "* 1.6"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-274",
					"maxclass" : "newobj",
					"numinlets" : 3,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1100.0, 854.0, 72.0, 22.0 ],
					"text" : "clip 0. 1."
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-275",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1100.0, 881.0, 82.0, 22.0 ],
					"text" : "prepend m7"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-276",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1186.0, 800.0, 155.0, 22.0 ],
					"text" : "expr ($f1 < 0.) * 3.141593"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-277",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1186.0, 827.0, 90.0, 22.0 ],
					"text" : "prepend ph7"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-278",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "float" ],
					"patching_rect" : [ 1250.0, 800.0, 48.0, 22.0 ],
					"text" : "abs 0."
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-279",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "float" ],
					"patching_rect" : [ 1250.0, 827.0, 48.0, 22.0 ],
					"text" : "* 1.6"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-280",
					"maxclass" : "newobj",
					"numinlets" : 3,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1250.0, 854.0, 72.0, 22.0 ],
					"text" : "clip 0. 1."
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-281",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1250.0, 881.0, 82.0, 22.0 ],
					"text" : "prepend m8"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-282",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1336.0, 800.0, 155.0, 22.0 ],
					"text" : "expr ($f1 < 0.) * 3.141593"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-283",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1336.0, 827.0, 90.0, 22.0 ],
					"text" : "prepend ph8"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-284",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "float" ],
					"patching_rect" : [ 1400.0, 800.0, 48.0, 22.0 ],
					"text" : "abs 0."
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-285",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "float" ],
					"patching_rect" : [ 1400.0, 827.0, 48.0, 22.0 ],
					"text" : "* 1.6"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-286",
					"maxclass" : "newobj",
					"numinlets" : 3,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1400.0, 854.0, 72.0, 22.0 ],
					"text" : "clip 0. 1."
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-287",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1400.0, 881.0, 82.0, 22.0 ],
					"text" : "prepend m9"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-288",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1486.0, 800.0, 155.0, 22.0 ],
					"text" : "expr ($f1 < 0.) * 3.141593"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-289",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1486.0, 827.0, 90.0, 22.0 ],
					"text" : "prepend ph9"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-290",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "float" ],
					"patching_rect" : [ 800.0, 930.0, 48.0, 22.0 ],
					"text" : "abs 0."
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-291",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "float" ],
					"patching_rect" : [ 800.0, 957.0, 48.0, 22.0 ],
					"text" : "* 1.6"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-292",
					"maxclass" : "newobj",
					"numinlets" : 3,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 800.0, 984.0, 72.0, 22.0 ],
					"text" : "clip 0. 1."
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-293",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 800.0, 1011.0, 82.0, 22.0 ],
					"text" : "prepend m10"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-294",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 886.0, 930.0, 155.0, 22.0 ],
					"text" : "expr ($f1 < 0.) * 3.141593"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-295",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 886.0, 957.0, 90.0, 22.0 ],
					"text" : "prepend ph10"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-296",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "float" ],
					"patching_rect" : [ 950.0, 930.0, 48.0, 22.0 ],
					"text" : "abs 0."
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-297",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "float" ],
					"patching_rect" : [ 950.0, 957.0, 48.0, 22.0 ],
					"text" : "* 1.6"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-298",
					"maxclass" : "newobj",
					"numinlets" : 3,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 950.0, 984.0, 72.0, 22.0 ],
					"text" : "clip 0. 1."
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-299",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 950.0, 1011.0, 82.0, 22.0 ],
					"text" : "prepend m11"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-300",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1036.0, 930.0, 155.0, 22.0 ],
					"text" : "expr ($f1 < 0.) * 3.141593"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-301",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1036.0, 957.0, 90.0, 22.0 ],
					"text" : "prepend ph11"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-302",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "float" ],
					"patching_rect" : [ 1100.0, 930.0, 48.0, 22.0 ],
					"text" : "abs 0."
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-303",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "float" ],
					"patching_rect" : [ 1100.0, 957.0, 48.0, 22.0 ],
					"text" : "* 1.6"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-304",
					"maxclass" : "newobj",
					"numinlets" : 3,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1100.0, 984.0, 72.0, 22.0 ],
					"text" : "clip 0. 1."
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-305",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1100.0, 1011.0, 82.0, 22.0 ],
					"text" : "prepend m12"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-306",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1186.0, 930.0, 155.0, 22.0 ],
					"text" : "expr ($f1 < 0.) * 3.141593"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-307",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1186.0, 957.0, 90.0, 22.0 ],
					"text" : "prepend ph12"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-308",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "float" ],
					"patching_rect" : [ 1250.0, 930.0, 48.0, 22.0 ],
					"text" : "abs 0."
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-309",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "float" ],
					"patching_rect" : [ 1250.0, 957.0, 48.0, 22.0 ],
					"text" : "* 1.6"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-310",
					"maxclass" : "newobj",
					"numinlets" : 3,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1250.0, 984.0, 72.0, 22.0 ],
					"text" : "clip 0. 1."
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-311",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1250.0, 1011.0, 82.0, 22.0 ],
					"text" : "prepend m13"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-312",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1336.0, 930.0, 155.0, 22.0 ],
					"text" : "expr ($f1 < 0.) * 3.141593"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-313",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1336.0, 957.0, 90.0, 22.0 ],
					"text" : "prepend ph13"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-314",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "float" ],
					"patching_rect" : [ 1400.0, 930.0, 48.0, 22.0 ],
					"text" : "abs 0."
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-315",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "float" ],
					"patching_rect" : [ 1400.0, 957.0, 48.0, 22.0 ],
					"text" : "* 1.6"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-316",
					"maxclass" : "newobj",
					"numinlets" : 3,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1400.0, 984.0, 72.0, 22.0 ],
					"text" : "clip 0. 1."
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-317",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1400.0, 1011.0, 82.0, 22.0 ],
					"text" : "prepend m14"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-318",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1486.0, 930.0, 155.0, 22.0 ],
					"text" : "expr ($f1 < 0.) * 3.141593"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-319",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1486.0, 957.0, 90.0, 22.0 ],
					"text" : "prepend ph14"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-320",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 800.0, 1065.0, 135.0, 22.0 ],
					"text" : "m15 0, ph15 0"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-321",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 1030.0, 385.0, 120.0, 20.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 1030.0, 375.0, 120.0, 20.0 ],
					"text" : "Master level (dB)"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "obj-322",
					"maxclass" : "flonum",
					"maximum" : 0.0,
					"minimum" : -60.0,
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 1150.0, 380.0, 75.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 1150.0, 370.0, 75.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-323",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1235.0, 380.0, 90.0, 22.0 ],
					"text" : "loadmess -10."
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-324",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1150.0, 410.0, 48.0, 22.0 ],
					"text" : "dbtoa"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-325",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1205.0, 410.0, 78.0, 22.0 ],
					"text" : "pack 0. 60"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-326",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 2,
					"outlettype" : [ "signal", "bang" ],
					"patching_rect" : [ 1290.0, 410.0, 48.0, 22.0 ],
					"text" : "line~"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-327",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 1210.0, 900.0, 40.0, 22.0 ],
					"text" : "*~"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-328",
					"maxclass" : "newobj",
					"numinlets" : 3,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 1260.0, 900.0, 95.0, 22.0 ],
					"text" : "clip~ -0.9 0.9"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-329",
					"maxclass" : "meter~",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "float" ],
					"patching_rect" : [ 1030.0, 455.0, 195.0, 16.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 1030.0, 420.0, 195.0, 16.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-330",
					"local" : 1,
					"maxclass" : "ezdac~",
					"numinlets" : 2,
					"numoutlets" : 0,
					"patching_rect" : [ 1157.0, 1039.0, 48.0, 48.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 1260.0, 405.0, 48.0, 48.0 ]
				}

			}
 ],
		"lines" : [ 			{
				"patchline" : 				{
					"destination" : [ "obj-124", 0 ],
					"order" : 0,
					"source" : [ "obj-123", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-8", 0 ],
					"order" : 1,
					"source" : [ "obj-123", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-327", 0 ],
					"hidden" : 1,
					"source" : [ "obj-200", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-204", 0 ],
					"source" : [ "obj-202", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-202", 0 ],
					"source" : [ "obj-203", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-200", 0 ],
					"hidden" : 1,
					"source" : [ "obj-204", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-207", 0 ],
					"source" : [ "obj-206", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-200", 0 ],
					"hidden" : 1,
					"source" : [ "obj-207", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-206", 0 ],
					"source" : [ "obj-208", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-211", 0 ],
					"source" : [ "obj-210", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-200", 0 ],
					"hidden" : 1,
					"source" : [ "obj-211", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-210", 0 ],
					"source" : [ "obj-212", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-215", 0 ],
					"source" : [ "obj-214", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-200", 0 ],
					"hidden" : 1,
					"source" : [ "obj-215", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-214", 0 ],
					"source" : [ "obj-216", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-219", 0 ],
					"source" : [ "obj-218", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-200", 0 ],
					"hidden" : 1,
					"source" : [ "obj-219", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-218", 0 ],
					"source" : [ "obj-220", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-223", 0 ],
					"source" : [ "obj-222", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-200", 0 ],
					"hidden" : 1,
					"source" : [ "obj-223", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-222", 0 ],
					"source" : [ "obj-224", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-227", 0 ],
					"source" : [ "obj-226", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-200", 0 ],
					"hidden" : 1,
					"source" : [ "obj-227", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-226", 0 ],
					"source" : [ "obj-228", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-200", 0 ],
					"hidden" : 1,
					"source" : [ "obj-229", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-231", 0 ],
					"source" : [ "obj-230", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-232", 0 ],
					"source" : [ "obj-231", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-233", 0 ],
					"source" : [ "obj-232", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-200", 0 ],
					"hidden" : 1,
					"source" : [ "obj-233", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-235", 0 ],
					"source" : [ "obj-234", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-200", 0 ],
					"hidden" : 1,
					"source" : [ "obj-235", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-237", 0 ],
					"source" : [ "obj-236", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-238", 0 ],
					"source" : [ "obj-237", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-239", 0 ],
					"source" : [ "obj-238", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-200", 0 ],
					"hidden" : 1,
					"source" : [ "obj-239", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-241", 0 ],
					"source" : [ "obj-240", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-200", 0 ],
					"hidden" : 1,
					"source" : [ "obj-241", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-243", 0 ],
					"source" : [ "obj-242", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-244", 0 ],
					"source" : [ "obj-243", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-245", 0 ],
					"source" : [ "obj-244", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-200", 0 ],
					"hidden" : 1,
					"source" : [ "obj-245", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-247", 0 ],
					"source" : [ "obj-246", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-200", 0 ],
					"hidden" : 1,
					"source" : [ "obj-247", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-249", 0 ],
					"source" : [ "obj-248", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-250", 0 ],
					"source" : [ "obj-249", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-251", 0 ],
					"source" : [ "obj-250", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-200", 0 ],
					"hidden" : 1,
					"source" : [ "obj-251", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-253", 0 ],
					"source" : [ "obj-252", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-200", 0 ],
					"hidden" : 1,
					"source" : [ "obj-253", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-255", 0 ],
					"source" : [ "obj-254", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-256", 0 ],
					"source" : [ "obj-255", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-257", 0 ],
					"source" : [ "obj-256", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-200", 0 ],
					"hidden" : 1,
					"source" : [ "obj-257", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-259", 0 ],
					"source" : [ "obj-258", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-200", 0 ],
					"hidden" : 1,
					"source" : [ "obj-259", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-261", 0 ],
					"source" : [ "obj-260", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-262", 0 ],
					"source" : [ "obj-261", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-263", 0 ],
					"source" : [ "obj-262", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-200", 0 ],
					"hidden" : 1,
					"source" : [ "obj-263", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-265", 0 ],
					"source" : [ "obj-264", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-200", 0 ],
					"hidden" : 1,
					"source" : [ "obj-265", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-267", 0 ],
					"source" : [ "obj-266", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-268", 0 ],
					"source" : [ "obj-267", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-269", 0 ],
					"source" : [ "obj-268", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-200", 0 ],
					"hidden" : 1,
					"source" : [ "obj-269", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-271", 0 ],
					"source" : [ "obj-270", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-200", 0 ],
					"hidden" : 1,
					"source" : [ "obj-271", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-273", 0 ],
					"source" : [ "obj-272", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-274", 0 ],
					"source" : [ "obj-273", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-275", 0 ],
					"source" : [ "obj-274", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-200", 0 ],
					"hidden" : 1,
					"source" : [ "obj-275", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-277", 0 ],
					"source" : [ "obj-276", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-200", 0 ],
					"hidden" : 1,
					"source" : [ "obj-277", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-279", 0 ],
					"source" : [ "obj-278", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-280", 0 ],
					"source" : [ "obj-279", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-281", 0 ],
					"source" : [ "obj-280", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-200", 0 ],
					"hidden" : 1,
					"source" : [ "obj-281", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-283", 0 ],
					"source" : [ "obj-282", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-200", 0 ],
					"hidden" : 1,
					"source" : [ "obj-283", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-285", 0 ],
					"source" : [ "obj-284", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-286", 0 ],
					"source" : [ "obj-285", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-287", 0 ],
					"source" : [ "obj-286", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-200", 0 ],
					"hidden" : 1,
					"source" : [ "obj-287", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-289", 0 ],
					"source" : [ "obj-288", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-200", 0 ],
					"hidden" : 1,
					"source" : [ "obj-289", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-291", 0 ],
					"source" : [ "obj-290", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-292", 0 ],
					"source" : [ "obj-291", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-293", 0 ],
					"source" : [ "obj-292", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-200", 0 ],
					"hidden" : 1,
					"source" : [ "obj-293", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-295", 0 ],
					"source" : [ "obj-294", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-200", 0 ],
					"hidden" : 1,
					"source" : [ "obj-295", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-297", 0 ],
					"source" : [ "obj-296", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-298", 0 ],
					"source" : [ "obj-297", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-299", 0 ],
					"source" : [ "obj-298", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-200", 0 ],
					"hidden" : 1,
					"source" : [ "obj-299", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-123", 0 ],
					"order" : 0,
					"source" : [ "obj-3", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-6", 0 ],
					"order" : 1,
					"source" : [ "obj-3", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-301", 0 ],
					"source" : [ "obj-300", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-200", 0 ],
					"hidden" : 1,
					"source" : [ "obj-301", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-303", 0 ],
					"source" : [ "obj-302", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-304", 0 ],
					"source" : [ "obj-303", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-305", 0 ],
					"source" : [ "obj-304", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-200", 0 ],
					"hidden" : 1,
					"source" : [ "obj-305", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-307", 0 ],
					"source" : [ "obj-306", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-200", 0 ],
					"hidden" : 1,
					"source" : [ "obj-307", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-309", 0 ],
					"source" : [ "obj-308", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-310", 0 ],
					"source" : [ "obj-309", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-311", 0 ],
					"source" : [ "obj-310", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-200", 0 ],
					"hidden" : 1,
					"source" : [ "obj-311", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-313", 0 ],
					"source" : [ "obj-312", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-200", 0 ],
					"hidden" : 1,
					"source" : [ "obj-313", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-315", 0 ],
					"source" : [ "obj-314", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-316", 0 ],
					"source" : [ "obj-315", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-317", 0 ],
					"source" : [ "obj-316", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-200", 0 ],
					"hidden" : 1,
					"source" : [ "obj-317", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-319", 0 ],
					"source" : [ "obj-318", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-200", 0 ],
					"hidden" : 1,
					"source" : [ "obj-319", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-200", 0 ],
					"hidden" : 1,
					"source" : [ "obj-320", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-324", 0 ],
					"source" : [ "obj-322", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-322", 0 ],
					"source" : [ "obj-323", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-325", 0 ],
					"source" : [ "obj-324", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-326", 0 ],
					"source" : [ "obj-325", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-327", 1 ],
					"source" : [ "obj-326", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-328", 0 ],
					"source" : [ "obj-327", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-329", 0 ],
					"order" : 2,
					"source" : [ "obj-328", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-330", 1 ],
					"order" : 0,
					"source" : [ "obj-328", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-330", 0 ],
					"order" : 1,
					"source" : [ "obj-328", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-229", 0 ],
					"order" : 1,
					"source" : [ "obj-4", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-320", 0 ],
					"order" : 0,
					"source" : [ "obj-4", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-5", 0 ],
					"order" : 2,
					"source" : [ "obj-4", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-3", 0 ],
					"source" : [ "obj-5", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-7", 0 ],
					"source" : [ "obj-6", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-124", 0 ],
					"order" : 0,
					"source" : [ "obj-7", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-8", 0 ],
					"order" : 1,
					"source" : [ "obj-7", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-10", 0 ],
					"source" : [ "obj-8", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-12", 0 ],
					"source" : [ "obj-8", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-14", 0 ],
					"source" : [ "obj-8", 2 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-16", 0 ],
					"source" : [ "obj-8", 3 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-18", 0 ],
					"source" : [ "obj-8", 4 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-230", 0 ],
					"order" : 1,
					"source" : [ "obj-8", 5 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-234", 0 ],
					"order" : 0,
					"source" : [ "obj-8", 5 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-236", 0 ],
					"order" : 1,
					"source" : [ "obj-8", 6 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-240", 0 ],
					"order" : 0,
					"source" : [ "obj-8", 6 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-242", 0 ],
					"order" : 1,
					"source" : [ "obj-8", 7 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-246", 0 ],
					"order" : 0,
					"source" : [ "obj-8", 7 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-248", 0 ],
					"order" : 1,
					"source" : [ "obj-8", 8 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-252", 0 ],
					"order" : 0,
					"source" : [ "obj-8", 8 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-254", 0 ],
					"order" : 1,
					"source" : [ "obj-8", 9 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-258", 0 ],
					"order" : 0,
					"source" : [ "obj-8", 9 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-260", 0 ],
					"order" : 1,
					"source" : [ "obj-8", 10 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-264", 0 ],
					"order" : 0,
					"source" : [ "obj-8", 10 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-266", 0 ],
					"order" : 1,
					"source" : [ "obj-8", 11 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-270", 0 ],
					"order" : 0,
					"source" : [ "obj-8", 11 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-272", 0 ],
					"order" : 1,
					"source" : [ "obj-8", 12 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-276", 0 ],
					"order" : 0,
					"source" : [ "obj-8", 12 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-278", 0 ],
					"order" : 1,
					"source" : [ "obj-8", 13 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-282", 0 ],
					"order" : 0,
					"source" : [ "obj-8", 13 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-284", 0 ],
					"order" : 1,
					"source" : [ "obj-8", 14 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-288", 0 ],
					"order" : 0,
					"source" : [ "obj-8", 14 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-290", 0 ],
					"order" : 1,
					"source" : [ "obj-8", 15 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-294", 0 ],
					"order" : 0,
					"source" : [ "obj-8", 15 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-296", 0 ],
					"order" : 1,
					"source" : [ "obj-8", 16 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-300", 0 ],
					"order" : 0,
					"source" : [ "obj-8", 16 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-302", 0 ],
					"order" : 1,
					"source" : [ "obj-8", 17 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-306", 0 ],
					"order" : 0,
					"source" : [ "obj-8", 17 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-308", 0 ],
					"order" : 1,
					"source" : [ "obj-8", 18 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-312", 0 ],
					"order" : 0,
					"source" : [ "obj-8", 18 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-314", 0 ],
					"order" : 1,
					"source" : [ "obj-8", 19 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-318", 0 ],
					"order" : 0,
					"source" : [ "obj-8", 19 ]
				}

			}
 ],
		"originid" : "pat-462",
		"dependency_cache" : [  ],
		"autosave" : 0
	}

}
