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
		"rect" : [ 50.0, 100.0, 1137.0, 798.0 ],
		"gridsize" : [ 15.0, 15.0 ],
		"boxes" : [ 			{
				"box" : 				{
					"id" : "obj-78",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "signal", "" ],
					"patching_rect" : [ 973.0, 246.0, 91.0, 22.0 ],
					"saved_object_attributes" : 					{
						"parameter_enable" : 0
					}
,
					"text" : "spat5.converb~"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "obj-70",
					"maxclass" : "flonum",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 831.0, 320.0, 50.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-71",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 808.0, 352.0, 130.0, 22.0 ],
					"text" : "prepend output_ceiling"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-55",
					"linecount" : 13,
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 979.0, 386.0, 232.0, 181.0 ],
					"text" : "Param purity(1);\nParam entropy(0);\nParam coherence(0);\nParam amp(0.2);\nParam default_freq(55);\nParam attack_ms(12);\nParam slow_decay_ms(900);\nParam fast_decay_ms(70);\nParam phase_smooth_ms(100);\nParam magnitude_smooth_ms(100);\nParam brightness(0.65);\nParam mix_voices(4);\nParam output_ceiling(0.85);"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-50",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 803.0, 213.0, 50.0, 22.0 ],
					"text" : "0."
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "obj-45",
					"maxclass" : "flonum",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 803.0, 179.0, 50.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-36",
					"linecount" : 2,
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 670.5, 212.5, 50.0, 35.0 ],
					"text" : "12.815329"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-24",
					"logfreq" : 1,
					"maxclass" : "spectroscope~",
					"monochrome" : 0,
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 497.0, 662.0, 130.0, 120.0 ],
					"sono" : 1
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-25",
					"logfreq" : 1,
					"maxclass" : "spectroscope~",
					"monochrome" : 0,
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 359.0, 662.0, 130.0, 120.0 ],
					"sono" : 1
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-23",
					"logfreq" : 1,
					"maxclass" : "spectroscope~",
					"monochrome" : 0,
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 222.0, 661.0, 130.0, 120.0 ],
					"sono" : 1
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-20",
					"logfreq" : 1,
					"maxclass" : "spectroscope~",
					"monochrome" : 0,
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 76.5, 661.0, 130.0, 120.0 ],
					"sono" : 1
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-7",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 573.0, 171.0, 112.0, 22.0 ],
					"text" : "prepend coherence"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-6",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 467.166668653488159, 171.0, 96.0, 22.0 ],
					"text" : "prepend entropy"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-106",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 734.0, 309.0, 79.0, 22.0 ],
					"text" : "prepend amp"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "obj-107",
					"maxclass" : "flonum",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 763.0, 272.0, 50.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"code" : "// QMW Density Field Quantum Resonator 16\n//\n// Gen~ codebox.\n// in1 is the carrier frequency in Hz.\n// m0..m15 excite sixteen resonant partials.\n// ph0..ph15 set smoothed per-partial timing/phase.\n// s0..s15 set lifetime: fast lanes flash, slow lanes ring.\n// h0..h15 are partial ratios. Defaults are harmonic 1..16, but these can\n// later be replaced by Hamiltonian energy-gap ratios.\n\nParam m0(0);\nParam m1(0);\nParam m2(0);\nParam m3(0);\nParam m4(0);\nParam m5(0);\nParam m6(0);\nParam m7(0);\nParam m8(0);\nParam m9(0);\nParam m10(0);\nParam m11(0);\nParam m12(0);\nParam m13(0);\nParam m14(0);\nParam m15(0);\n\nParam ph0(0);\nParam ph1(0);\nParam ph2(0);\nParam ph3(0);\nParam ph4(0);\nParam ph5(0);\nParam ph6(0);\nParam ph7(0);\nParam ph8(0);\nParam ph9(0);\nParam ph10(0);\nParam ph11(0);\nParam ph12(0);\nParam ph13(0);\nParam ph14(0);\nParam ph15(0);\n\nParam s0(0);\nParam s1(0);\nParam s2(0);\nParam s3(0);\nParam s4(0);\nParam s5(0);\nParam s6(0);\nParam s7(0);\nParam s8(0);\nParam s9(0);\nParam s10(0);\nParam s11(0);\nParam s12(0);\nParam s13(0);\nParam s14(0);\nParam s15(0);\n\nParam h0(1);\nParam h1(2);\nParam h2(3);\nParam h3(4);\nParam h4(5);\nParam h5(6);\nParam h6(7);\nParam h7(8);\nParam h8(9);\nParam h9(10);\nParam h10(11);\nParam h11(12);\nParam h12(13);\nParam h13(14);\nParam h14(15);\nParam h15(16);\n\nParam purity(1);\nParam entropy(0);\nParam coherence(0);\nParam amp(0.2);\nParam default_freq(55);\nParam attack_ms(12);\nParam slow_decay_ms(900);\nParam fast_decay_ms(70);\nParam phase_smooth_ms(100);\nParam magnitude_smooth_ms(100);\nParam brightness(0.65);\nParam mix_voices(4);\nParam output_ceiling(0.85);\n\nHistory p0(0);\nHistory p1(0);\nHistory p2(0);\nHistory p3(0);\nHistory p4(0);\nHistory p5(0);\nHistory p6(0);\nHistory p7(0);\nHistory p8(0);\nHistory p9(0);\nHistory p10(0);\nHistory p11(0);\nHistory p12(0);\nHistory p13(0);\nHistory p14(0);\nHistory p15(0);\n\nHistory e0(0);\nHistory e1(0);\nHistory e2(0);\nHistory e3(0);\nHistory e4(0);\nHistory e5(0);\nHistory e6(0);\nHistory e7(0);\nHistory e8(0);\nHistory e9(0);\nHistory e10(0);\nHistory e11(0);\nHistory e12(0);\nHistory e13(0);\nHistory e14(0);\nHistory e15(0);\n\nHistory sm0(0);\nHistory sm1(0);\nHistory sm2(0);\nHistory sm3(0);\nHistory sm4(0);\nHistory sm5(0);\nHistory sm6(0);\nHistory sm7(0);\nHistory sm8(0);\nHistory sm9(0);\nHistory sm10(0);\nHistory sm11(0);\nHistory sm12(0);\nHistory sm13(0);\nHistory sm14(0);\nHistory sm15(0);\n\nHistory sph0(0);\nHistory sph1(0);\nHistory sph2(0);\nHistory sph3(0);\nHistory sph4(0);\nHistory sph5(0);\nHistory sph6(0);\nHistory sph7(0);\nHistory sph8(0);\nHistory sph9(0);\nHistory sph10(0);\nHistory sph11(0);\nHistory sph12(0);\nHistory sph13(0);\nHistory sph14(0);\nHistory sph15(0);\n\nfreq = (in1 > 0) * in1 + (in1 <= 0) * default_freq;\npur = clamp(purity, 0, 1);\nent = clamp(entropy, 0, 1);\ncoh = clamp(coherence, 0, 1);\n\nmag_ms = max(magnitude_smooth_ms, 0.1);\nmag_coeff = exp(-1 / (mag_ms * 0.001 * samplerate));\n\ntm0 = clamp(m0, 0, 1);\ntm1 = clamp(m1, 0, 1);\ntm2 = clamp(m2, 0, 1);\ntm3 = clamp(m3, 0, 1);\ntm4 = clamp(m4, 0, 1);\ntm5 = clamp(m5, 0, 1);\ntm6 = clamp(m6, 0, 1);\ntm7 = clamp(m7, 0, 1);\ntm8 = clamp(m8, 0, 1);\ntm9 = clamp(m9, 0, 1);\ntm10 = clamp(m10, 0, 1);\ntm11 = clamp(m11, 0, 1);\ntm12 = clamp(m12, 0, 1);\ntm13 = clamp(m13, 0, 1);\ntm14 = clamp(m14, 0, 1);\ntm15 = clamp(m15, 0, 1);\n\nsm0 = tm0 + mag_coeff * (sm0 - tm0);\nsm1 = tm1 + mag_coeff * (sm1 - tm1);\nsm2 = tm2 + mag_coeff * (sm2 - tm2);\nsm3 = tm3 + mag_coeff * (sm3 - tm3);\nsm4 = tm4 + mag_coeff * (sm4 - tm4);\nsm5 = tm5 + mag_coeff * (sm5 - tm5);\nsm6 = tm6 + mag_coeff * (sm6 - tm6);\nsm7 = tm7 + mag_coeff * (sm7 - tm7);\nsm8 = tm8 + mag_coeff * (sm8 - tm8);\nsm9 = tm9 + mag_coeff * (sm9 - tm9);\nsm10 = tm10 + mag_coeff * (sm10 - tm10);\nsm11 = tm11 + mag_coeff * (sm11 - tm11);\nsm12 = tm12 + mag_coeff * (sm12 - tm12);\nsm13 = tm13 + mag_coeff * (sm13 - tm13);\nsm14 = tm14 + mag_coeff * (sm14 - tm14);\nsm15 = tm15 + mag_coeff * (sm15 - tm15);\n\nphase_ms = max(phase_smooth_ms, 0.1);\nphase_coeff = exp(-1 / (phase_ms * 0.001 * samplerate));\n\ndph0 = atan2(sin(ph0 - sph0), cos(ph0 - sph0));\ndph1 = atan2(sin(ph1 - sph1), cos(ph1 - sph1));\ndph2 = atan2(sin(ph2 - sph2), cos(ph2 - sph2));\ndph3 = atan2(sin(ph3 - sph3), cos(ph3 - sph3));\ndph4 = atan2(sin(ph4 - sph4), cos(ph4 - sph4));\ndph5 = atan2(sin(ph5 - sph5), cos(ph5 - sph5));\ndph6 = atan2(sin(ph6 - sph6), cos(ph6 - sph6));\ndph7 = atan2(sin(ph7 - sph7), cos(ph7 - sph7));\ndph8 = atan2(sin(ph8 - sph8), cos(ph8 - sph8));\ndph9 = atan2(sin(ph9 - sph9), cos(ph9 - sph9));\ndph10 = atan2(sin(ph10 - sph10), cos(ph10 - sph10));\ndph11 = atan2(sin(ph11 - sph11), cos(ph11 - sph11));\ndph12 = atan2(sin(ph12 - sph12), cos(ph12 - sph12));\ndph13 = atan2(sin(ph13 - sph13), cos(ph13 - sph13));\ndph14 = atan2(sin(ph14 - sph14), cos(ph14 - sph14));\ndph15 = atan2(sin(ph15 - sph15), cos(ph15 - sph15));\n\nsph0 = sph0 + (1 - phase_coeff) * dph0;\nsph1 = sph1 + (1 - phase_coeff) * dph1;\nsph2 = sph2 + (1 - phase_coeff) * dph2;\nsph3 = sph3 + (1 - phase_coeff) * dph3;\nsph4 = sph4 + (1 - phase_coeff) * dph4;\nsph5 = sph5 + (1 - phase_coeff) * dph5;\nsph6 = sph6 + (1 - phase_coeff) * dph6;\nsph7 = sph7 + (1 - phase_coeff) * dph7;\nsph8 = sph8 + (1 - phase_coeff) * dph8;\nsph9 = sph9 + (1 - phase_coeff) * dph9;\nsph10 = sph10 + (1 - phase_coeff) * dph10;\nsph11 = sph11 + (1 - phase_coeff) * dph11;\nsph12 = sph12 + (1 - phase_coeff) * dph12;\nsph13 = sph13 + (1 - phase_coeff) * dph13;\nsph14 = sph14 + (1 - phase_coeff) * dph14;\nsph15 = sph15 + (1 - phase_coeff) * dph15;\n\natk_ms = max(attack_ms * mix(1.35, 0.65, coh), 0.1);\natk_coeff = exp(-1 / (atk_ms * 0.001 * samplerate));\n\nspd0 = clamp(abs(s0), 0, 1);\nspd1 = clamp(abs(s1), 0, 1);\nspd2 = clamp(abs(s2), 0, 1);\nspd3 = clamp(abs(s3), 0, 1);\nspd4 = clamp(abs(s4), 0, 1);\nspd5 = clamp(abs(s5), 0, 1);\nspd6 = clamp(abs(s6), 0, 1);\nspd7 = clamp(abs(s7), 0, 1);\nspd8 = clamp(abs(s8), 0, 1);\nspd9 = clamp(abs(s9), 0, 1);\nspd10 = clamp(abs(s10), 0, 1);\nspd11 = clamp(abs(s11), 0, 1);\nspd12 = clamp(abs(s12), 0, 1);\nspd13 = clamp(abs(s13), 0, 1);\nspd14 = clamp(abs(s14), 0, 1);\nspd15 = clamp(abs(s15), 0, 1);\n\ndec0 = mix(slow_decay_ms, fast_decay_ms, spd0);\ndec1 = mix(slow_decay_ms, fast_decay_ms, spd1);\ndec2 = mix(slow_decay_ms, fast_decay_ms, spd2);\ndec3 = mix(slow_decay_ms, fast_decay_ms, spd3);\ndec4 = mix(slow_decay_ms, fast_decay_ms, spd4);\ndec5 = mix(slow_decay_ms, fast_decay_ms, spd5);\ndec6 = mix(slow_decay_ms, fast_decay_ms, spd6);\ndec7 = mix(slow_decay_ms, fast_decay_ms, spd7);\ndec8 = mix(slow_decay_ms, fast_decay_ms, spd8);\ndec9 = mix(slow_decay_ms, fast_decay_ms, spd9);\ndec10 = mix(slow_decay_ms, fast_decay_ms, spd10);\ndec11 = mix(slow_decay_ms, fast_decay_ms, spd11);\ndec12 = mix(slow_decay_ms, fast_decay_ms, spd12);\ndec13 = mix(slow_decay_ms, fast_decay_ms, spd13);\ndec14 = mix(slow_decay_ms, fast_decay_ms, spd14);\ndec15 = mix(slow_decay_ms, fast_decay_ms, spd15);\n\ndc0 = exp(-1 / (max(dec0, 0.1) * 0.001 * samplerate));\ndc1 = exp(-1 / (max(dec1, 0.1) * 0.001 * samplerate));\ndc2 = exp(-1 / (max(dec2, 0.1) * 0.001 * samplerate));\ndc3 = exp(-1 / (max(dec3, 0.1) * 0.001 * samplerate));\ndc4 = exp(-1 / (max(dec4, 0.1) * 0.001 * samplerate));\ndc5 = exp(-1 / (max(dec5, 0.1) * 0.001 * samplerate));\ndc6 = exp(-1 / (max(dec6, 0.1) * 0.001 * samplerate));\ndc7 = exp(-1 / (max(dec7, 0.1) * 0.001 * samplerate));\ndc8 = exp(-1 / (max(dec8, 0.1) * 0.001 * samplerate));\ndc9 = exp(-1 / (max(dec9, 0.1) * 0.001 * samplerate));\ndc10 = exp(-1 / (max(dec10, 0.1) * 0.001 * samplerate));\ndc11 = exp(-1 / (max(dec11, 0.1) * 0.001 * samplerate));\ndc12 = exp(-1 / (max(dec12, 0.1) * 0.001 * samplerate));\ndc13 = exp(-1 / (max(dec13, 0.1) * 0.001 * samplerate));\ndc14 = exp(-1 / (max(dec14, 0.1) * 0.001 * samplerate));\ndc15 = exp(-1 / (max(dec15, 0.1) * 0.001 * samplerate));\n\n// Higher entropy lifts weaker modes. Higher purity makes excitation more selective.\nexc_shape = mix(0.55, 1.6, pur);\nt0 = pow(sm0 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt1 = pow(sm1 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt2 = pow(sm2 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt3 = pow(sm3 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt4 = pow(sm4 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt5 = pow(sm5 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt6 = pow(sm6 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt7 = pow(sm7 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt8 = pow(sm8 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt9 = pow(sm9 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt10 = pow(sm10 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt11 = pow(sm11 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt12 = pow(sm12 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt13 = pow(sm13 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt14 = pow(sm14 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt15 = pow(sm15 + 0.00001, exc_shape) * mix(0.35, 1, ent);\n\ne0 = (t0 > e0) * (t0 + atk_coeff * (e0 - t0)) + (t0 <= e0) * (t0 + dc0 * (e0 - t0));\ne1 = (t1 > e1) * (t1 + atk_coeff * (e1 - t1)) + (t1 <= e1) * (t1 + dc1 * (e1 - t1));\ne2 = (t2 > e2) * (t2 + atk_coeff * (e2 - t2)) + (t2 <= e2) * (t2 + dc2 * (e2 - t2));\ne3 = (t3 > e3) * (t3 + atk_coeff * (e3 - t3)) + (t3 <= e3) * (t3 + dc3 * (e3 - t3));\ne4 = (t4 > e4) * (t4 + atk_coeff * (e4 - t4)) + (t4 <= e4) * (t4 + dc4 * (e4 - t4));\ne5 = (t5 > e5) * (t5 + atk_coeff * (e5 - t5)) + (t5 <= e5) * (t5 + dc5 * (e5 - t5));\ne6 = (t6 > e6) * (t6 + atk_coeff * (e6 - t6)) + (t6 <= e6) * (t6 + dc6 * (e6 - t6));\ne7 = (t7 > e7) * (t7 + atk_coeff * (e7 - t7)) + (t7 <= e7) * (t7 + dc7 * (e7 - t7));\ne8 = (t8 > e8) * (t8 + atk_coeff * (e8 - t8)) + (t8 <= e8) * (t8 + dc8 * (e8 - t8));\ne9 = (t9 > e9) * (t9 + atk_coeff * (e9 - t9)) + (t9 <= e9) * (t9 + dc9 * (e9 - t9));\ne10 = (t10 > e10) * (t10 + atk_coeff * (e10 - t10)) + (t10 <= e10) * (t10 + dc10 * (e10 - t10));\ne11 = (t11 > e11) * (t11 + atk_coeff * (e11 - t11)) + (t11 <= e11) * (t11 + dc11 * (e11 - t11));\ne12 = (t12 > e12) * (t12 + atk_coeff * (e12 - t12)) + (t12 <= e12) * (t12 + dc12 * (e12 - t12));\ne13 = (t13 > e13) * (t13 + atk_coeff * (e13 - t13)) + (t13 <= e13) * (t13 + dc13 * (e13 - t13));\ne14 = (t14 > e14) * (t14 + atk_coeff * (e14 - t14)) + (t14 <= e14) * (t14 + dc14 * (e14 - t14));\ne15 = (t15 > e15) * (t15 + atk_coeff * (e15 - t15)) + (t15 <= e15) * (t15 + dc15 * (e15 - t15));\n\nbright = clamp(brightness + ent * 0.25, 0, 1);\n\np0 = fract(p0 + freq * max(h0, 0.01) / samplerate);\np1 = fract(p1 + freq * max(h1, 0.01) / samplerate);\np2 = fract(p2 + freq * max(h2, 0.01) / samplerate);\np3 = fract(p3 + freq * max(h3, 0.01) / samplerate);\np4 = fract(p4 + freq * max(h4, 0.01) / samplerate);\np5 = fract(p5 + freq * max(h5, 0.01) / samplerate);\np6 = fract(p6 + freq * max(h6, 0.01) / samplerate);\np7 = fract(p7 + freq * max(h7, 0.01) / samplerate);\np8 = fract(p8 + freq * max(h8, 0.01) / samplerate);\np9 = fract(p9 + freq * max(h9, 0.01) / samplerate);\np10 = fract(p10 + freq * max(h10, 0.01) / samplerate);\np11 = fract(p11 + freq * max(h11, 0.01) / samplerate);\np12 = fract(p12 + freq * max(h12, 0.01) / samplerate);\np13 = fract(p13 + freq * max(h13, 0.01) / samplerate);\np14 = fract(p14 + freq * max(h14, 0.01) / samplerate);\np15 = fract(p15 + freq * max(h15, 0.01) / samplerate);\n\ntwopi = 6.283185307179586;\npartials =\n    e0 * sin(twopi * p0 + sph0) / pow(max(h0, 1), bright) +\n    e1 * sin(twopi * p1 + sph1) / pow(max(h1, 1), bright) +\n    e2 * sin(twopi * p2 + sph2) / pow(max(h2, 1), bright) +\n    e3 * sin(twopi * p3 + sph3) / pow(max(h3, 1), bright) +\n    e4 * sin(twopi * p4 + sph4) / pow(max(h4, 1), bright) +\n    e5 * sin(twopi * p5 + sph5) / pow(max(h5, 1), bright) +\n    e6 * sin(twopi * p6 + sph6) / pow(max(h6, 1), bright) +\n    e7 * sin(twopi * p7 + sph7) / pow(max(h7, 1), bright) +\n    e8 * sin(twopi * p8 + sph8) / pow(max(h8, 1), bright) +\n    e9 * sin(twopi * p9 + sph9) / pow(max(h9, 1), bright) +\n    e10 * sin(twopi * p10 + sph10) / pow(max(h10, 1), bright) +\n    e11 * sin(twopi * p11 + sph11) / pow(max(h11, 1), bright) +\n    e12 * sin(twopi * p12 + sph12) / pow(max(h12, 1), bright) +\n    e13 * sin(twopi * p13 + sph13) / pow(max(h13, 1), bright) +\n    e14 * sin(twopi * p14 + sph14) / pow(max(h14, 1), bright) +\n    e15 * sin(twopi * p15 + sph15) / pow(max(h15, 1), bright);\n\nvoice_scale = 1 / sqrt(max(mix_voices, 1));\nsig = partials;\n\nout1 = sig * amp * output_ceiling * voice_scale;\nout2 = e0 + e1 + e2 + e3 + e4 + e5 + e6 + e7 + e8 + e9 + e10 + e11 + e12 + e13 + e14 + e15;\nout3 = freq;\n",
					"fontface" : 0,
					"fontname" : "<Monospaced>",
					"fontsize" : 12.0,
					"id" : "obj-108",
					"maxclass" : "gen.codebox~",
					"numinlets" : 1,
					"numoutlets" : 3,
					"outlettype" : [ "signal", "signal", "signal" ],
					"patching_rect" : [ 674.0, 390.0, 143.0, 25.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-109",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 680.0, 309.0, 31.0, 22.0 ],
					"text" : "sig~"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "obj-110",
					"maxclass" : "flonum",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 679.0, 265.0, 50.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "obj-111",
					"maxclass" : "flonum",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 859.0, 462.0, 50.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-112",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 752.0, 489.0, 34.0, 22.0 ],
					"text" : "*~ 1."
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-105",
					"maxclass" : "preset",
					"numinlets" : 1,
					"numoutlets" : 5,
					"outlettype" : [ "preset", "int", "preset", "int", "" ],
					"patching_rect" : [ 845.0, 147.0, 100.0, 40.0 ],
					"preset_data" : [ 						{
							"number" : 1,
							"data" : [ 5, "obj-59", "number", "float", 0.25, 5, "obj-75", "number", "float", 40.0, 5, "obj-30", "number", "float", 0.25, 5, "obj-40", "number", "float", 0.25, 5, "obj-16", "number", "float", 2.0, 5, "obj-58", "number", "float", 80.0, 5, "obj-22", "number", "float", 2.0, 5, "obj-65", "number", "float", 160.0, 5, "obj-62", "number", "float", 2.0, 5, "obj-102", "toggle", "int", 0, 5, "obj-100", "number", "float", 0.435000002384186, 5, "obj-97", "number", "float", 0.381999999284744, 5, "obj-95", "number", "float", 0.739000022411346, 5, "obj-94", "number", "float", 0.600000023841858, 5, "obj-93", "number", "float", 0.953000009059906, 5, "obj-91", "toggle", "int", 0, 5, "obj-88", "number", "float", 0.0, 5, "obj-87", "number", "float", 0.0, 5, "obj-86", "number", "float", 1.0, 5, "obj-84", "number", "float", 0.5 ]
						}
, 						{
							"number" : 2,
							"data" : [ 5, "obj-59", "number", "float", 0.25, 5, "obj-75", "number", "float", 55.0, 5, "obj-30", "number", "float", 0.25, 5, "obj-40", "number", "float", 0.25, 5, "obj-16", "number", "float", 0.419999986886978, 5, "obj-58", "number", "float", 109.599998474121094, 5, "obj-22", "number", "float", 0.551999986171722, 5, "obj-65", "number", "float", 142.0, 5, "obj-62", "number", "float", 0.432000011205673, 5, "obj-102", "toggle", "int", 0, 5, "obj-100", "number", "float", 0.787000000476837, 5, "obj-97", "number", "float", 0.531000018119812, 5, "obj-95", "number", "float", 0.739000022411346, 5, "obj-94", "number", "float", 0.100000001490116, 5, "obj-93", "number", "float", 0.953000009059906, 5, "obj-91", "toggle", "int", 0, 5, "obj-88", "number", "float", 0.0, 5, "obj-87", "number", "float", 0.0, 5, "obj-86", "number", "float", 1.0, 5, "obj-84", "number", "float", 0.0, 5, "obj-111", "number", "float", 0.25, 5, "obj-110", "number", "float", 157.100006103515625, 5, "obj-107", "number", "float", 0.317999988794327 ]
						}
, 						{
							"number" : 3,
							"data" : [ 5, "obj-59", "number", "float", 0.25, 5, "obj-75", "number", "float", 25.0, 5, "obj-30", "number", "float", 0.25, 5, "obj-40", "number", "float", 0.25, 5, "obj-16", "number", "float", 1.0, 5, "obj-58", "number", "float", 37.700000762939453, 5, "obj-22", "number", "float", 1.0, 5, "obj-65", "number", "float", 50.299999237060547, 5, "obj-62", "number", "float", 1.0, 5, "obj-102", "toggle", "int", 0, 5, "obj-100", "number", "float", 0.0, 5, "obj-97", "number", "float", 0.277999997138977, 5, "obj-95", "number", "float", 0.0, 5, "obj-94", "number", "float", 0.0, 5, "obj-93", "number", "float", 0.621999979019165, 5, "obj-91", "toggle", "int", 0, 5, "obj-88", "number", "float", 0.0, 5, "obj-87", "number", "float", 0.0, 5, "obj-86", "number", "float", 0.736999988555908, 5, "obj-84", "number", "float", 0.0, 5, "obj-111", "number", "float", 0.25, 5, "obj-110", "number", "float", 63.0, 5, "obj-107", "number", "float", 1.0, 5, "obj-45", "number", "float", 1.0 ]
						}
 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-82",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 651.0, 659.0, 80.0, 20.0 ],
					"text" : "meta control"
				}

			}
, 			{
				"box" : 				{
					"fontface" : 1,
					"id" : "obj-83",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 762.0, 659.0, 117.0, 20.0 ],
					"text" : "main parameters:"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "obj-84",
					"maxclass" : "flonum",
					"maximum" : 1.0,
					"minimum" : 0.0,
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 965.0, 691.0, 51.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-85",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 965.0, 732.0, 41.0, 22.0 ],
					"text" : "hp $1"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "obj-86",
					"maxclass" : "flonum",
					"maximum" : 1.0,
					"minimum" : 0.0,
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 814.0, 767.0, 50.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-37",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 814.0, 798.0, 51.0, 22.0 ],
					"text" : "gain $1"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "obj-87",
					"maxclass" : "flonum",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 931.0, 768.0, 50.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "obj-88",
					"maxclass" : "flonum",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 878.0, 768.0, 50.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-89",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 878.0, 798.0, 73.0, 22.0 ],
					"text" : "pak 0.3 0.5"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-90",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 878.0, 829.0, 58.0, 22.0 ],
					"text" : "lfo $1 $2"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-91",
					"maxclass" : "toggle",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "int" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 1031.0, 691.0, 24.0, 24.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-92",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1031.0, 732.0, 63.0, 22.0 ],
					"text" : "freeze $1"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "obj-93",
					"maxclass" : "flonum",
					"minimum" : 0.0,
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 762.0, 691.0, 50.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "obj-94",
					"maxclass" : "flonum",
					"maximum" : 1.0,
					"minimum" : 0.0,
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 901.0, 691.0, 50.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-18",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 901.0, 732.0, 59.0, 22.0 ],
					"text" : "damp $1"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "obj-95",
					"maxclass" : "flonum",
					"maximum" : 1.0,
					"minimum" : 0.0,
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 731.0, 767.0, 50.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-96",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 731.0, 798.0, 75.0, 22.0 ],
					"text" : "diffusion $1"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "obj-97",
					"maxclass" : "flonum",
					"maximum" : 1.0,
					"minimum" : 0.0,
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 825.0, 691.0, 50.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-98",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 825.0, 732.0, 65.0, 22.0 ],
					"text" : "drywet $1"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-99",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 762.0, 732.0, 51.0, 22.0 ],
					"text" : "time $1"
				}

			}
, 			{
				"box" : 				{
					"bgcolor" : [ 0.811764705882353, 0.086274509803922, 0.086274509803922, 1.0 ],
					"format" : 6,
					"id" : "obj-100",
					"maxclass" : "flonum",
					"maximum" : 1.0,
					"minimum" : 0.0,
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 661.0, 691.0, 50.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-101",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 661.0, 732.0, 61.0, 22.0 ],
					"text" : "space $1"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-102",
					"maxclass" : "toggle",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "int" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 655.0, 767.0, 24.0, 24.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-103",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 655.0, 798.0, 70.0, 22.0 ],
					"text" : "bypass $1"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-17",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 2,
					"outlettype" : [ "signal", "signal" ],
					"patching_rect" : [ 758.333337306976318, 561.0, 71.0, 22.0 ],
					"text" : "vb.mi.verb~"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-60",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 494.0, 315.0, 79.0, 22.0 ],
					"text" : "prepend amp"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "obj-62",
					"maxclass" : "flonum",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 523.0, 278.0, 50.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"code" : "// QMW Desity Field Quantum Resonator 16\n//\n// Gen~ codebox.\n// in1 is the carrier frequency in Hz.\n// m0..m15 excite sixteen resonant partials.\n// ph0..ph15 set smoothed per-partial timing/phase.\n// s0..s15 set lifetime: fast lanes flash, slow lanes ring.\n// h0..h15 are partial ratios. Defaults are harmonic 1..16, but these can\n// later be replaced by Hamiltonian energy-gap ratios.\n\nParam m0(0);\nParam m1(0);\nParam m2(0);\nParam m3(0);\nParam m4(0);\nParam m5(0);\nParam m6(0);\nParam m7(0);\nParam m8(0);\nParam m9(0);\nParam m10(0);\nParam m11(0);\nParam m12(0);\nParam m13(0);\nParam m14(0);\nParam m15(0);\n\nParam ph0(0);\nParam ph1(0);\nParam ph2(0);\nParam ph3(0);\nParam ph4(0);\nParam ph5(0);\nParam ph6(0);\nParam ph7(0);\nParam ph8(0);\nParam ph9(0);\nParam ph10(0);\nParam ph11(0);\nParam ph12(0);\nParam ph13(0);\nParam ph14(0);\nParam ph15(0);\n\nParam s0(0);\nParam s1(0);\nParam s2(0);\nParam s3(0);\nParam s4(0);\nParam s5(0);\nParam s6(0);\nParam s7(0);\nParam s8(0);\nParam s9(0);\nParam s10(0);\nParam s11(0);\nParam s12(0);\nParam s13(0);\nParam s14(0);\nParam s15(0);\n\nParam h0(1);\nParam h1(2);\nParam h2(3);\nParam h3(4);\nParam h4(5);\nParam h5(6);\nParam h6(7);\nParam h7(8);\nParam h8(9);\nParam h9(10);\nParam h10(11);\nParam h11(12);\nParam h12(13);\nParam h13(14);\nParam h14(15);\nParam h15(16);\n\nParam purity(1);\nParam entropy(0);\nParam coherence(0);\nParam amp(0.2);\nParam default_freq(55);\nParam attack_ms(12);\nParam slow_decay_ms(900);\nParam fast_decay_ms(70);\nParam phase_smooth_ms(100);\nParam magnitude_smooth_ms(100);\nParam brightness(0.65);\nParam mix_voices(4);\nParam output_ceiling(0.85);\n\nHistory p0(0);\nHistory p1(0);\nHistory p2(0);\nHistory p3(0);\nHistory p4(0);\nHistory p5(0);\nHistory p6(0);\nHistory p7(0);\nHistory p8(0);\nHistory p9(0);\nHistory p10(0);\nHistory p11(0);\nHistory p12(0);\nHistory p13(0);\nHistory p14(0);\nHistory p15(0);\n\nHistory e0(0);\nHistory e1(0);\nHistory e2(0);\nHistory e3(0);\nHistory e4(0);\nHistory e5(0);\nHistory e6(0);\nHistory e7(0);\nHistory e8(0);\nHistory e9(0);\nHistory e10(0);\nHistory e11(0);\nHistory e12(0);\nHistory e13(0);\nHistory e14(0);\nHistory e15(0);\n\nHistory sm0(0);\nHistory sm1(0);\nHistory sm2(0);\nHistory sm3(0);\nHistory sm4(0);\nHistory sm5(0);\nHistory sm6(0);\nHistory sm7(0);\nHistory sm8(0);\nHistory sm9(0);\nHistory sm10(0);\nHistory sm11(0);\nHistory sm12(0);\nHistory sm13(0);\nHistory sm14(0);\nHistory sm15(0);\n\nHistory sph0(0);\nHistory sph1(0);\nHistory sph2(0);\nHistory sph3(0);\nHistory sph4(0);\nHistory sph5(0);\nHistory sph6(0);\nHistory sph7(0);\nHistory sph8(0);\nHistory sph9(0);\nHistory sph10(0);\nHistory sph11(0);\nHistory sph12(0);\nHistory sph13(0);\nHistory sph14(0);\nHistory sph15(0);\n\nfreq = (in1 > 0) * in1 + (in1 <= 0) * default_freq;\npur = clamp(purity, 0, 1);\nent = clamp(entropy, 0, 1);\ncoh = clamp(coherence, 0, 1);\n\nmag_ms = max(magnitude_smooth_ms, 0.1);\nmag_coeff = exp(-1 / (mag_ms * 0.001 * samplerate));\n\ntm0 = clamp(m0, 0, 1);\ntm1 = clamp(m1, 0, 1);\ntm2 = clamp(m2, 0, 1);\ntm3 = clamp(m3, 0, 1);\ntm4 = clamp(m4, 0, 1);\ntm5 = clamp(m5, 0, 1);\ntm6 = clamp(m6, 0, 1);\ntm7 = clamp(m7, 0, 1);\ntm8 = clamp(m8, 0, 1);\ntm9 = clamp(m9, 0, 1);\ntm10 = clamp(m10, 0, 1);\ntm11 = clamp(m11, 0, 1);\ntm12 = clamp(m12, 0, 1);\ntm13 = clamp(m13, 0, 1);\ntm14 = clamp(m14, 0, 1);\ntm15 = clamp(m15, 0, 1);\n\nsm0 = tm0 + mag_coeff * (sm0 - tm0);\nsm1 = tm1 + mag_coeff * (sm1 - tm1);\nsm2 = tm2 + mag_coeff * (sm2 - tm2);\nsm3 = tm3 + mag_coeff * (sm3 - tm3);\nsm4 = tm4 + mag_coeff * (sm4 - tm4);\nsm5 = tm5 + mag_coeff * (sm5 - tm5);\nsm6 = tm6 + mag_coeff * (sm6 - tm6);\nsm7 = tm7 + mag_coeff * (sm7 - tm7);\nsm8 = tm8 + mag_coeff * (sm8 - tm8);\nsm9 = tm9 + mag_coeff * (sm9 - tm9);\nsm10 = tm10 + mag_coeff * (sm10 - tm10);\nsm11 = tm11 + mag_coeff * (sm11 - tm11);\nsm12 = tm12 + mag_coeff * (sm12 - tm12);\nsm13 = tm13 + mag_coeff * (sm13 - tm13);\nsm14 = tm14 + mag_coeff * (sm14 - tm14);\nsm15 = tm15 + mag_coeff * (sm15 - tm15);\n\nphase_ms = max(phase_smooth_ms, 0.1);\nphase_coeff = exp(-1 / (phase_ms * 0.001 * samplerate));\n\ndph0 = atan2(sin(ph0 - sph0), cos(ph0 - sph0));\ndph1 = atan2(sin(ph1 - sph1), cos(ph1 - sph1));\ndph2 = atan2(sin(ph2 - sph2), cos(ph2 - sph2));\ndph3 = atan2(sin(ph3 - sph3), cos(ph3 - sph3));\ndph4 = atan2(sin(ph4 - sph4), cos(ph4 - sph4));\ndph5 = atan2(sin(ph5 - sph5), cos(ph5 - sph5));\ndph6 = atan2(sin(ph6 - sph6), cos(ph6 - sph6));\ndph7 = atan2(sin(ph7 - sph7), cos(ph7 - sph7));\ndph8 = atan2(sin(ph8 - sph8), cos(ph8 - sph8));\ndph9 = atan2(sin(ph9 - sph9), cos(ph9 - sph9));\ndph10 = atan2(sin(ph10 - sph10), cos(ph10 - sph10));\ndph11 = atan2(sin(ph11 - sph11), cos(ph11 - sph11));\ndph12 = atan2(sin(ph12 - sph12), cos(ph12 - sph12));\ndph13 = atan2(sin(ph13 - sph13), cos(ph13 - sph13));\ndph14 = atan2(sin(ph14 - sph14), cos(ph14 - sph14));\ndph15 = atan2(sin(ph15 - sph15), cos(ph15 - sph15));\n\nsph0 = sph0 + (1 - phase_coeff) * dph0;\nsph1 = sph1 + (1 - phase_coeff) * dph1;\nsph2 = sph2 + (1 - phase_coeff) * dph2;\nsph3 = sph3 + (1 - phase_coeff) * dph3;\nsph4 = sph4 + (1 - phase_coeff) * dph4;\nsph5 = sph5 + (1 - phase_coeff) * dph5;\nsph6 = sph6 + (1 - phase_coeff) * dph6;\nsph7 = sph7 + (1 - phase_coeff) * dph7;\nsph8 = sph8 + (1 - phase_coeff) * dph8;\nsph9 = sph9 + (1 - phase_coeff) * dph9;\nsph10 = sph10 + (1 - phase_coeff) * dph10;\nsph11 = sph11 + (1 - phase_coeff) * dph11;\nsph12 = sph12 + (1 - phase_coeff) * dph12;\nsph13 = sph13 + (1 - phase_coeff) * dph13;\nsph14 = sph14 + (1 - phase_coeff) * dph14;\nsph15 = sph15 + (1 - phase_coeff) * dph15;\n\natk_ms = max(attack_ms * mix(1.35, 0.65, coh), 0.1);\natk_coeff = exp(-1 / (atk_ms * 0.001 * samplerate));\n\nspd0 = clamp(abs(s0), 0, 1);\nspd1 = clamp(abs(s1), 0, 1);\nspd2 = clamp(abs(s2), 0, 1);\nspd3 = clamp(abs(s3), 0, 1);\nspd4 = clamp(abs(s4), 0, 1);\nspd5 = clamp(abs(s5), 0, 1);\nspd6 = clamp(abs(s6), 0, 1);\nspd7 = clamp(abs(s7), 0, 1);\nspd8 = clamp(abs(s8), 0, 1);\nspd9 = clamp(abs(s9), 0, 1);\nspd10 = clamp(abs(s10), 0, 1);\nspd11 = clamp(abs(s11), 0, 1);\nspd12 = clamp(abs(s12), 0, 1);\nspd13 = clamp(abs(s13), 0, 1);\nspd14 = clamp(abs(s14), 0, 1);\nspd15 = clamp(abs(s15), 0, 1);\n\ndec0 = mix(slow_decay_ms, fast_decay_ms, spd0);\ndec1 = mix(slow_decay_ms, fast_decay_ms, spd1);\ndec2 = mix(slow_decay_ms, fast_decay_ms, spd2);\ndec3 = mix(slow_decay_ms, fast_decay_ms, spd3);\ndec4 = mix(slow_decay_ms, fast_decay_ms, spd4);\ndec5 = mix(slow_decay_ms, fast_decay_ms, spd5);\ndec6 = mix(slow_decay_ms, fast_decay_ms, spd6);\ndec7 = mix(slow_decay_ms, fast_decay_ms, spd7);\ndec8 = mix(slow_decay_ms, fast_decay_ms, spd8);\ndec9 = mix(slow_decay_ms, fast_decay_ms, spd9);\ndec10 = mix(slow_decay_ms, fast_decay_ms, spd10);\ndec11 = mix(slow_decay_ms, fast_decay_ms, spd11);\ndec12 = mix(slow_decay_ms, fast_decay_ms, spd12);\ndec13 = mix(slow_decay_ms, fast_decay_ms, spd13);\ndec14 = mix(slow_decay_ms, fast_decay_ms, spd14);\ndec15 = mix(slow_decay_ms, fast_decay_ms, spd15);\n\ndc0 = exp(-1 / (max(dec0, 0.1) * 0.001 * samplerate));\ndc1 = exp(-1 / (max(dec1, 0.1) * 0.001 * samplerate));\ndc2 = exp(-1 / (max(dec2, 0.1) * 0.001 * samplerate));\ndc3 = exp(-1 / (max(dec3, 0.1) * 0.001 * samplerate));\ndc4 = exp(-1 / (max(dec4, 0.1) * 0.001 * samplerate));\ndc5 = exp(-1 / (max(dec5, 0.1) * 0.001 * samplerate));\ndc6 = exp(-1 / (max(dec6, 0.1) * 0.001 * samplerate));\ndc7 = exp(-1 / (max(dec7, 0.1) * 0.001 * samplerate));\ndc8 = exp(-1 / (max(dec8, 0.1) * 0.001 * samplerate));\ndc9 = exp(-1 / (max(dec9, 0.1) * 0.001 * samplerate));\ndc10 = exp(-1 / (max(dec10, 0.1) * 0.001 * samplerate));\ndc11 = exp(-1 / (max(dec11, 0.1) * 0.001 * samplerate));\ndc12 = exp(-1 / (max(dec12, 0.1) * 0.001 * samplerate));\ndc13 = exp(-1 / (max(dec13, 0.1) * 0.001 * samplerate));\ndc14 = exp(-1 / (max(dec14, 0.1) * 0.001 * samplerate));\ndc15 = exp(-1 / (max(dec15, 0.1) * 0.001 * samplerate));\n\n// Higher entropy lifts weaker modes. Higher purity makes excitation more selective.\nexc_shape = mix(0.55, 1.6, pur);\nt0 = pow(sm0 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt1 = pow(sm1 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt2 = pow(sm2 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt3 = pow(sm3 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt4 = pow(sm4 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt5 = pow(sm5 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt6 = pow(sm6 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt7 = pow(sm7 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt8 = pow(sm8 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt9 = pow(sm9 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt10 = pow(sm10 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt11 = pow(sm11 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt12 = pow(sm12 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt13 = pow(sm13 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt14 = pow(sm14 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt15 = pow(sm15 + 0.00001, exc_shape) * mix(0.35, 1, ent);\n\ne0 = (t0 > e0) * (t0 + atk_coeff * (e0 - t0)) + (t0 <= e0) * (t0 + dc0 * (e0 - t0));\ne1 = (t1 > e1) * (t1 + atk_coeff * (e1 - t1)) + (t1 <= e1) * (t1 + dc1 * (e1 - t1));\ne2 = (t2 > e2) * (t2 + atk_coeff * (e2 - t2)) + (t2 <= e2) * (t2 + dc2 * (e2 - t2));\ne3 = (t3 > e3) * (t3 + atk_coeff * (e3 - t3)) + (t3 <= e3) * (t3 + dc3 * (e3 - t3));\ne4 = (t4 > e4) * (t4 + atk_coeff * (e4 - t4)) + (t4 <= e4) * (t4 + dc4 * (e4 - t4));\ne5 = (t5 > e5) * (t5 + atk_coeff * (e5 - t5)) + (t5 <= e5) * (t5 + dc5 * (e5 - t5));\ne6 = (t6 > e6) * (t6 + atk_coeff * (e6 - t6)) + (t6 <= e6) * (t6 + dc6 * (e6 - t6));\ne7 = (t7 > e7) * (t7 + atk_coeff * (e7 - t7)) + (t7 <= e7) * (t7 + dc7 * (e7 - t7));\ne8 = (t8 > e8) * (t8 + atk_coeff * (e8 - t8)) + (t8 <= e8) * (t8 + dc8 * (e8 - t8));\ne9 = (t9 > e9) * (t9 + atk_coeff * (e9 - t9)) + (t9 <= e9) * (t9 + dc9 * (e9 - t9));\ne10 = (t10 > e10) * (t10 + atk_coeff * (e10 - t10)) + (t10 <= e10) * (t10 + dc10 * (e10 - t10));\ne11 = (t11 > e11) * (t11 + atk_coeff * (e11 - t11)) + (t11 <= e11) * (t11 + dc11 * (e11 - t11));\ne12 = (t12 > e12) * (t12 + atk_coeff * (e12 - t12)) + (t12 <= e12) * (t12 + dc12 * (e12 - t12));\ne13 = (t13 > e13) * (t13 + atk_coeff * (e13 - t13)) + (t13 <= e13) * (t13 + dc13 * (e13 - t13));\ne14 = (t14 > e14) * (t14 + atk_coeff * (e14 - t14)) + (t14 <= e14) * (t14 + dc14 * (e14 - t14));\ne15 = (t15 > e15) * (t15 + atk_coeff * (e15 - t15)) + (t15 <= e15) * (t15 + dc15 * (e15 - t15));\n\nbright = clamp(brightness + ent * 0.25, 0, 1);\n\np0 = fract(p0 + freq * max(h0, 0.01) / samplerate);\np1 = fract(p1 + freq * max(h1, 0.01) / samplerate);\np2 = fract(p2 + freq * max(h2, 0.01) / samplerate);\np3 = fract(p3 + freq * max(h3, 0.01) / samplerate);\np4 = fract(p4 + freq * max(h4, 0.01) / samplerate);\np5 = fract(p5 + freq * max(h5, 0.01) / samplerate);\np6 = fract(p6 + freq * max(h6, 0.01) / samplerate);\np7 = fract(p7 + freq * max(h7, 0.01) / samplerate);\np8 = fract(p8 + freq * max(h8, 0.01) / samplerate);\np9 = fract(p9 + freq * max(h9, 0.01) / samplerate);\np10 = fract(p10 + freq * max(h10, 0.01) / samplerate);\np11 = fract(p11 + freq * max(h11, 0.01) / samplerate);\np12 = fract(p12 + freq * max(h12, 0.01) / samplerate);\np13 = fract(p13 + freq * max(h13, 0.01) / samplerate);\np14 = fract(p14 + freq * max(h14, 0.01) / samplerate);\np15 = fract(p15 + freq * max(h15, 0.01) / samplerate);\n\ntwopi = 6.283185307179586;\npartials =\n    e0 * sin(twopi * p0 + sph0) / pow(max(h0, 1), bright) +\n    e1 * sin(twopi * p1 + sph1) / pow(max(h1, 1), bright) +\n    e2 * sin(twopi * p2 + sph2) / pow(max(h2, 1), bright) +\n    e3 * sin(twopi * p3 + sph3) / pow(max(h3, 1), bright) +\n    e4 * sin(twopi * p4 + sph4) / pow(max(h4, 1), bright) +\n    e5 * sin(twopi * p5 + sph5) / pow(max(h5, 1), bright) +\n    e6 * sin(twopi * p6 + sph6) / pow(max(h6, 1), bright) +\n    e7 * sin(twopi * p7 + sph7) / pow(max(h7, 1), bright) +\n    e8 * sin(twopi * p8 + sph8) / pow(max(h8, 1), bright) +\n    e9 * sin(twopi * p9 + sph9) / pow(max(h9, 1), bright) +\n    e10 * sin(twopi * p10 + sph10) / pow(max(h10, 1), bright) +\n    e11 * sin(twopi * p11 + sph11) / pow(max(h11, 1), bright) +\n    e12 * sin(twopi * p12 + sph12) / pow(max(h12, 1), bright) +\n    e13 * sin(twopi * p13 + sph13) / pow(max(h13, 1), bright) +\n    e14 * sin(twopi * p14 + sph14) / pow(max(h14, 1), bright) +\n    e15 * sin(twopi * p15 + sph15) / pow(max(h15, 1), bright);\n\nvoice_scale = 1 / sqrt(max(mix_voices, 1));\nsig = partials;\n\nout1 = sig * amp * output_ceiling * voice_scale;\nout2 = e0 + e1 + e2 + e3 + e4 + e5 + e6 + e7 + e8 + e9 + e10 + e11 + e12 + e13 + e14 + e15;\nout3 = freq;\n",
					"fontface" : 0,
					"fontname" : "<Monospaced>",
					"fontsize" : 12.0,
					"id" : "obj-63",
					"maxclass" : "gen.codebox~",
					"numinlets" : 1,
					"numoutlets" : 3,
					"outlettype" : [ "signal", "signal", "signal" ],
					"patching_rect" : [ 416.0, 386.5, 165.0, 32.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-64",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 440.0, 315.0, 31.0, 22.0 ],
					"text" : "sig~"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "obj-65",
					"maxclass" : "flonum",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 439.0, 271.0, 50.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-21",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 265.0, 337.0, 79.0, 22.0 ],
					"text" : "prepend amp"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "obj-22",
					"maxclass" : "flonum",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 295.0, 299.0, 50.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"code" : "// QMW Density Field Quantum Resonator 16\n//\n// Gen~ codebox.\n// in1 is the carrier frequency in Hz.\n// m0..m15 excite sixteen resonant partials.\n// ph0..ph15 set smoothed per-partial timing/phase.\n// s0..s15 set lifetime: fast lanes flash, slow lanes ring.\n// h0..h15 are partial ratios. Defaults are harmonic 1..16, but these can\n// later be replaced by Hamiltonian energy-gap ratios.\n\nParam m0(0);\nParam m1(0);\nParam m2(0);\nParam m3(0);\nParam m4(0);\nParam m5(0);\nParam m6(0);\nParam m7(0);\nParam m8(0);\nParam m9(0);\nParam m10(0);\nParam m11(0);\nParam m12(0);\nParam m13(0);\nParam m14(0);\nParam m15(0);\n\nParam ph0(0);\nParam ph1(0);\nParam ph2(0);\nParam ph3(0);\nParam ph4(0);\nParam ph5(0);\nParam ph6(0);\nParam ph7(0);\nParam ph8(0);\nParam ph9(0);\nParam ph10(0);\nParam ph11(0);\nParam ph12(0);\nParam ph13(0);\nParam ph14(0);\nParam ph15(0);\n\nParam s0(0);\nParam s1(0);\nParam s2(0);\nParam s3(0);\nParam s4(0);\nParam s5(0);\nParam s6(0);\nParam s7(0);\nParam s8(0);\nParam s9(0);\nParam s10(0);\nParam s11(0);\nParam s12(0);\nParam s13(0);\nParam s14(0);\nParam s15(0);\n\nParam h0(1);\nParam h1(2);\nParam h2(3);\nParam h3(4);\nParam h4(5);\nParam h5(6);\nParam h6(7);\nParam h7(8);\nParam h8(9);\nParam h9(10);\nParam h10(11);\nParam h11(12);\nParam h12(13);\nParam h13(14);\nParam h14(15);\nParam h15(16);\n\nParam purity(1);\nParam entropy(0);\nParam coherence(0);\nParam amp(0.2);\nParam default_freq(55);\nParam attack_ms(12);\nParam slow_decay_ms(900);\nParam fast_decay_ms(70);\nParam phase_smooth_ms(100);\nParam magnitude_smooth_ms(100);\nParam brightness(0.65);\nParam mix_voices(4);\nParam output_ceiling(0.85);\n\nHistory p0(0);\nHistory p1(0);\nHistory p2(0);\nHistory p3(0);\nHistory p4(0);\nHistory p5(0);\nHistory p6(0);\nHistory p7(0);\nHistory p8(0);\nHistory p9(0);\nHistory p10(0);\nHistory p11(0);\nHistory p12(0);\nHistory p13(0);\nHistory p14(0);\nHistory p15(0);\n\nHistory e0(0);\nHistory e1(0);\nHistory e2(0);\nHistory e3(0);\nHistory e4(0);\nHistory e5(0);\nHistory e6(0);\nHistory e7(0);\nHistory e8(0);\nHistory e9(0);\nHistory e10(0);\nHistory e11(0);\nHistory e12(0);\nHistory e13(0);\nHistory e14(0);\nHistory e15(0);\n\nHistory sm0(0);\nHistory sm1(0);\nHistory sm2(0);\nHistory sm3(0);\nHistory sm4(0);\nHistory sm5(0);\nHistory sm6(0);\nHistory sm7(0);\nHistory sm8(0);\nHistory sm9(0);\nHistory sm10(0);\nHistory sm11(0);\nHistory sm12(0);\nHistory sm13(0);\nHistory sm14(0);\nHistory sm15(0);\n\nHistory sph0(0);\nHistory sph1(0);\nHistory sph2(0);\nHistory sph3(0);\nHistory sph4(0);\nHistory sph5(0);\nHistory sph6(0);\nHistory sph7(0);\nHistory sph8(0);\nHistory sph9(0);\nHistory sph10(0);\nHistory sph11(0);\nHistory sph12(0);\nHistory sph13(0);\nHistory sph14(0);\nHistory sph15(0);\n\nfreq = (in1 > 0) * in1 + (in1 <= 0) * default_freq;\npur = clamp(purity, 0, 1);\nent = clamp(entropy, 0, 1);\ncoh = clamp(coherence, 0, 1);\n\nmag_ms = max(magnitude_smooth_ms, 0.1);\nmag_coeff = exp(-1 / (mag_ms * 0.001 * samplerate));\n\ntm0 = clamp(m0, 0, 1);\ntm1 = clamp(m1, 0, 1);\ntm2 = clamp(m2, 0, 1);\ntm3 = clamp(m3, 0, 1);\ntm4 = clamp(m4, 0, 1);\ntm5 = clamp(m5, 0, 1);\ntm6 = clamp(m6, 0, 1);\ntm7 = clamp(m7, 0, 1);\ntm8 = clamp(m8, 0, 1);\ntm9 = clamp(m9, 0, 1);\ntm10 = clamp(m10, 0, 1);\ntm11 = clamp(m11, 0, 1);\ntm12 = clamp(m12, 0, 1);\ntm13 = clamp(m13, 0, 1);\ntm14 = clamp(m14, 0, 1);\ntm15 = clamp(m15, 0, 1);\n\nsm0 = tm0 + mag_coeff * (sm0 - tm0);\nsm1 = tm1 + mag_coeff * (sm1 - tm1);\nsm2 = tm2 + mag_coeff * (sm2 - tm2);\nsm3 = tm3 + mag_coeff * (sm3 - tm3);\nsm4 = tm4 + mag_coeff * (sm4 - tm4);\nsm5 = tm5 + mag_coeff * (sm5 - tm5);\nsm6 = tm6 + mag_coeff * (sm6 - tm6);\nsm7 = tm7 + mag_coeff * (sm7 - tm7);\nsm8 = tm8 + mag_coeff * (sm8 - tm8);\nsm9 = tm9 + mag_coeff * (sm9 - tm9);\nsm10 = tm10 + mag_coeff * (sm10 - tm10);\nsm11 = tm11 + mag_coeff * (sm11 - tm11);\nsm12 = tm12 + mag_coeff * (sm12 - tm12);\nsm13 = tm13 + mag_coeff * (sm13 - tm13);\nsm14 = tm14 + mag_coeff * (sm14 - tm14);\nsm15 = tm15 + mag_coeff * (sm15 - tm15);\n\nphase_ms = max(phase_smooth_ms, 0.1);\nphase_coeff = exp(-1 / (phase_ms * 0.001 * samplerate));\n\ndph0 = atan2(sin(ph0 - sph0), cos(ph0 - sph0));\ndph1 = atan2(sin(ph1 - sph1), cos(ph1 - sph1));\ndph2 = atan2(sin(ph2 - sph2), cos(ph2 - sph2));\ndph3 = atan2(sin(ph3 - sph3), cos(ph3 - sph3));\ndph4 = atan2(sin(ph4 - sph4), cos(ph4 - sph4));\ndph5 = atan2(sin(ph5 - sph5), cos(ph5 - sph5));\ndph6 = atan2(sin(ph6 - sph6), cos(ph6 - sph6));\ndph7 = atan2(sin(ph7 - sph7), cos(ph7 - sph7));\ndph8 = atan2(sin(ph8 - sph8), cos(ph8 - sph8));\ndph9 = atan2(sin(ph9 - sph9), cos(ph9 - sph9));\ndph10 = atan2(sin(ph10 - sph10), cos(ph10 - sph10));\ndph11 = atan2(sin(ph11 - sph11), cos(ph11 - sph11));\ndph12 = atan2(sin(ph12 - sph12), cos(ph12 - sph12));\ndph13 = atan2(sin(ph13 - sph13), cos(ph13 - sph13));\ndph14 = atan2(sin(ph14 - sph14), cos(ph14 - sph14));\ndph15 = atan2(sin(ph15 - sph15), cos(ph15 - sph15));\n\nsph0 = sph0 + (1 - phase_coeff) * dph0;\nsph1 = sph1 + (1 - phase_coeff) * dph1;\nsph2 = sph2 + (1 - phase_coeff) * dph2;\nsph3 = sph3 + (1 - phase_coeff) * dph3;\nsph4 = sph4 + (1 - phase_coeff) * dph4;\nsph5 = sph5 + (1 - phase_coeff) * dph5;\nsph6 = sph6 + (1 - phase_coeff) * dph6;\nsph7 = sph7 + (1 - phase_coeff) * dph7;\nsph8 = sph8 + (1 - phase_coeff) * dph8;\nsph9 = sph9 + (1 - phase_coeff) * dph9;\nsph10 = sph10 + (1 - phase_coeff) * dph10;\nsph11 = sph11 + (1 - phase_coeff) * dph11;\nsph12 = sph12 + (1 - phase_coeff) * dph12;\nsph13 = sph13 + (1 - phase_coeff) * dph13;\nsph14 = sph14 + (1 - phase_coeff) * dph14;\nsph15 = sph15 + (1 - phase_coeff) * dph15;\n\natk_ms = max(attack_ms * mix(1.35, 0.65, coh), 0.1);\natk_coeff = exp(-1 / (atk_ms * 0.001 * samplerate));\n\nspd0 = clamp(abs(s0), 0, 1);\nspd1 = clamp(abs(s1), 0, 1);\nspd2 = clamp(abs(s2), 0, 1);\nspd3 = clamp(abs(s3), 0, 1);\nspd4 = clamp(abs(s4), 0, 1);\nspd5 = clamp(abs(s5), 0, 1);\nspd6 = clamp(abs(s6), 0, 1);\nspd7 = clamp(abs(s7), 0, 1);\nspd8 = clamp(abs(s8), 0, 1);\nspd9 = clamp(abs(s9), 0, 1);\nspd10 = clamp(abs(s10), 0, 1);\nspd11 = clamp(abs(s11), 0, 1);\nspd12 = clamp(abs(s12), 0, 1);\nspd13 = clamp(abs(s13), 0, 1);\nspd14 = clamp(abs(s14), 0, 1);\nspd15 = clamp(abs(s15), 0, 1);\n\ndec0 = mix(slow_decay_ms, fast_decay_ms, spd0);\ndec1 = mix(slow_decay_ms, fast_decay_ms, spd1);\ndec2 = mix(slow_decay_ms, fast_decay_ms, spd2);\ndec3 = mix(slow_decay_ms, fast_decay_ms, spd3);\ndec4 = mix(slow_decay_ms, fast_decay_ms, spd4);\ndec5 = mix(slow_decay_ms, fast_decay_ms, spd5);\ndec6 = mix(slow_decay_ms, fast_decay_ms, spd6);\ndec7 = mix(slow_decay_ms, fast_decay_ms, spd7);\ndec8 = mix(slow_decay_ms, fast_decay_ms, spd8);\ndec9 = mix(slow_decay_ms, fast_decay_ms, spd9);\ndec10 = mix(slow_decay_ms, fast_decay_ms, spd10);\ndec11 = mix(slow_decay_ms, fast_decay_ms, spd11);\ndec12 = mix(slow_decay_ms, fast_decay_ms, spd12);\ndec13 = mix(slow_decay_ms, fast_decay_ms, spd13);\ndec14 = mix(slow_decay_ms, fast_decay_ms, spd14);\ndec15 = mix(slow_decay_ms, fast_decay_ms, spd15);\n\ndc0 = exp(-1 / (max(dec0, 0.1) * 0.001 * samplerate));\ndc1 = exp(-1 / (max(dec1, 0.1) * 0.001 * samplerate));\ndc2 = exp(-1 / (max(dec2, 0.1) * 0.001 * samplerate));\ndc3 = exp(-1 / (max(dec3, 0.1) * 0.001 * samplerate));\ndc4 = exp(-1 / (max(dec4, 0.1) * 0.001 * samplerate));\ndc5 = exp(-1 / (max(dec5, 0.1) * 0.001 * samplerate));\ndc6 = exp(-1 / (max(dec6, 0.1) * 0.001 * samplerate));\ndc7 = exp(-1 / (max(dec7, 0.1) * 0.001 * samplerate));\ndc8 = exp(-1 / (max(dec8, 0.1) * 0.001 * samplerate));\ndc9 = exp(-1 / (max(dec9, 0.1) * 0.001 * samplerate));\ndc10 = exp(-1 / (max(dec10, 0.1) * 0.001 * samplerate));\ndc11 = exp(-1 / (max(dec11, 0.1) * 0.001 * samplerate));\ndc12 = exp(-1 / (max(dec12, 0.1) * 0.001 * samplerate));\ndc13 = exp(-1 / (max(dec13, 0.1) * 0.001 * samplerate));\ndc14 = exp(-1 / (max(dec14, 0.1) * 0.001 * samplerate));\ndc15 = exp(-1 / (max(dec15, 0.1) * 0.001 * samplerate));\n\n// Higher entropy lifts weaker modes. Higher purity makes excitation more selective.\nexc_shape = mix(0.55, 1.6, pur);\nt0 = pow(sm0 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt1 = pow(sm1 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt2 = pow(sm2 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt3 = pow(sm3 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt4 = pow(sm4 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt5 = pow(sm5 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt6 = pow(sm6 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt7 = pow(sm7 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt8 = pow(sm8 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt9 = pow(sm9 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt10 = pow(sm10 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt11 = pow(sm11 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt12 = pow(sm12 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt13 = pow(sm13 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt14 = pow(sm14 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt15 = pow(sm15 + 0.00001, exc_shape) * mix(0.35, 1, ent);\n\ne0 = (t0 > e0) * (t0 + atk_coeff * (e0 - t0)) + (t0 <= e0) * (t0 + dc0 * (e0 - t0));\ne1 = (t1 > e1) * (t1 + atk_coeff * (e1 - t1)) + (t1 <= e1) * (t1 + dc1 * (e1 - t1));\ne2 = (t2 > e2) * (t2 + atk_coeff * (e2 - t2)) + (t2 <= e2) * (t2 + dc2 * (e2 - t2));\ne3 = (t3 > e3) * (t3 + atk_coeff * (e3 - t3)) + (t3 <= e3) * (t3 + dc3 * (e3 - t3));\ne4 = (t4 > e4) * (t4 + atk_coeff * (e4 - t4)) + (t4 <= e4) * (t4 + dc4 * (e4 - t4));\ne5 = (t5 > e5) * (t5 + atk_coeff * (e5 - t5)) + (t5 <= e5) * (t5 + dc5 * (e5 - t5));\ne6 = (t6 > e6) * (t6 + atk_coeff * (e6 - t6)) + (t6 <= e6) * (t6 + dc6 * (e6 - t6));\ne7 = (t7 > e7) * (t7 + atk_coeff * (e7 - t7)) + (t7 <= e7) * (t7 + dc7 * (e7 - t7));\ne8 = (t8 > e8) * (t8 + atk_coeff * (e8 - t8)) + (t8 <= e8) * (t8 + dc8 * (e8 - t8));\ne9 = (t9 > e9) * (t9 + atk_coeff * (e9 - t9)) + (t9 <= e9) * (t9 + dc9 * (e9 - t9));\ne10 = (t10 > e10) * (t10 + atk_coeff * (e10 - t10)) + (t10 <= e10) * (t10 + dc10 * (e10 - t10));\ne11 = (t11 > e11) * (t11 + atk_coeff * (e11 - t11)) + (t11 <= e11) * (t11 + dc11 * (e11 - t11));\ne12 = (t12 > e12) * (t12 + atk_coeff * (e12 - t12)) + (t12 <= e12) * (t12 + dc12 * (e12 - t12));\ne13 = (t13 > e13) * (t13 + atk_coeff * (e13 - t13)) + (t13 <= e13) * (t13 + dc13 * (e13 - t13));\ne14 = (t14 > e14) * (t14 + atk_coeff * (e14 - t14)) + (t14 <= e14) * (t14 + dc14 * (e14 - t14));\ne15 = (t15 > e15) * (t15 + atk_coeff * (e15 - t15)) + (t15 <= e15) * (t15 + dc15 * (e15 - t15));\n\nbright = clamp(brightness + ent * 0.25, 0, 1);\n\np0 = fract(p0 + freq * max(h0, 0.01) / samplerate);\np1 = fract(p1 + freq * max(h1, 0.01) / samplerate);\np2 = fract(p2 + freq * max(h2, 0.01) / samplerate);\np3 = fract(p3 + freq * max(h3, 0.01) / samplerate);\np4 = fract(p4 + freq * max(h4, 0.01) / samplerate);\np5 = fract(p5 + freq * max(h5, 0.01) / samplerate);\np6 = fract(p6 + freq * max(h6, 0.01) / samplerate);\np7 = fract(p7 + freq * max(h7, 0.01) / samplerate);\np8 = fract(p8 + freq * max(h8, 0.01) / samplerate);\np9 = fract(p9 + freq * max(h9, 0.01) / samplerate);\np10 = fract(p10 + freq * max(h10, 0.01) / samplerate);\np11 = fract(p11 + freq * max(h11, 0.01) / samplerate);\np12 = fract(p12 + freq * max(h12, 0.01) / samplerate);\np13 = fract(p13 + freq * max(h13, 0.01) / samplerate);\np14 = fract(p14 + freq * max(h14, 0.01) / samplerate);\np15 = fract(p15 + freq * max(h15, 0.01) / samplerate);\n\ntwopi = 6.283185307179586;\npartials =\n    e0 * sin(twopi * p0 + sph0) / pow(max(h0, 1), bright) +\n    e1 * sin(twopi * p1 + sph1) / pow(max(h1, 1), bright) +\n    e2 * sin(twopi * p2 + sph2) / pow(max(h2, 1), bright) +\n    e3 * sin(twopi * p3 + sph3) / pow(max(h3, 1), bright) +\n    e4 * sin(twopi * p4 + sph4) / pow(max(h4, 1), bright) +\n    e5 * sin(twopi * p5 + sph5) / pow(max(h5, 1), bright) +\n    e6 * sin(twopi * p6 + sph6) / pow(max(h6, 1), bright) +\n    e7 * sin(twopi * p7 + sph7) / pow(max(h7, 1), bright) +\n    e8 * sin(twopi * p8 + sph8) / pow(max(h8, 1), bright) +\n    e9 * sin(twopi * p9 + sph9) / pow(max(h9, 1), bright) +\n    e10 * sin(twopi * p10 + sph10) / pow(max(h10, 1), bright) +\n    e11 * sin(twopi * p11 + sph11) / pow(max(h11, 1), bright) +\n    e12 * sin(twopi * p12 + sph12) / pow(max(h12, 1), bright) +\n    e13 * sin(twopi * p13 + sph13) / pow(max(h13, 1), bright) +\n    e14 * sin(twopi * p14 + sph14) / pow(max(h14, 1), bright) +\n    e15 * sin(twopi * p15 + sph15) / pow(max(h15, 1), bright);\n\nvoice_scale = 1 / sqrt(max(mix_voices, 1));\nsig = partials;\n\nout1 = sig * amp * output_ceiling * voice_scale;\nout2 = e0 + e1 + e2 + e3 + e4 + e5 + e6 + e7 + e8 + e9 + e10 + e11 + e12 + e13 + e14 + e15;\nout3 = freq;\n",
					"fontface" : 0,
					"fontname" : "<Monospaced>",
					"fontsize" : 12.0,
					"id" : "obj-39",
					"maxclass" : "gen.codebox~",
					"numinlets" : 1,
					"numoutlets" : 3,
					"outlettype" : [ "signal", "signal", "signal" ],
					"patching_rect" : [ 212.0, 387.0, 141.0, 31.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-42",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 212.0, 337.0, 31.0, 22.0 ],
					"text" : "sig~"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "obj-58",
					"maxclass" : "flonum",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 211.0, 293.0, 50.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-14",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 96.0, 333.0, 79.0, 22.0 ],
					"text" : "prepend amp"
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
					"patching_rect" : [ 96.0, 306.0, 50.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"code" : "// QMW Density Field Quantum Resonator 16\n//\n// Gen~ codebox.\n// in1 is the carrier frequency in Hz.\n// m0..m15 excite sixteen resonant partials.\n// ph0..ph15 set smoothed per-partial timing/phase.\n// s0..s15 set lifetime: fast lanes flash, slow lanes ring.\n// h0..h15 are partial ratios. Defaults are harmonic 1..16, but these can\n// later be replaced by Hamiltonian energy-gap ratios.\n\nParam m0(0);\nParam m1(0);\nParam m2(0);\nParam m3(0);\nParam m4(0);\nParam m5(0);\nParam m6(0);\nParam m7(0);\nParam m8(0);\nParam m9(0);\nParam m10(0);\nParam m11(0);\nParam m12(0);\nParam m13(0);\nParam m14(0);\nParam m15(0);\n\nParam ph0(0);\nParam ph1(0);\nParam ph2(0);\nParam ph3(0);\nParam ph4(0);\nParam ph5(0);\nParam ph6(0);\nParam ph7(0);\nParam ph8(0);\nParam ph9(0);\nParam ph10(0);\nParam ph11(0);\nParam ph12(0);\nParam ph13(0);\nParam ph14(0);\nParam ph15(0);\n\nParam s0(0);\nParam s1(0);\nParam s2(0);\nParam s3(0);\nParam s4(0);\nParam s5(0);\nParam s6(0);\nParam s7(0);\nParam s8(0);\nParam s9(0);\nParam s10(0);\nParam s11(0);\nParam s12(0);\nParam s13(0);\nParam s14(0);\nParam s15(0);\n\nParam h0(1);\nParam h1(2);\nParam h2(3);\nParam h3(4);\nParam h4(5);\nParam h5(6);\nParam h6(7);\nParam h7(8);\nParam h8(9);\nParam h9(10);\nParam h10(11);\nParam h11(12);\nParam h12(13);\nParam h13(14);\nParam h14(15);\nParam h15(16);\n\nParam purity(1);\nParam entropy(0);\nParam coherence(0);\nParam amp(0.2);\nParam default_freq(55);\nParam attack_ms(12);\nParam slow_decay_ms(900);\nParam fast_decay_ms(70);\nParam phase_smooth_ms(100);\nParam magnitude_smooth_ms(100);\nParam brightness(0.65);\nParam mix_voices(4);\nParam output_ceiling(0.85);\n\nHistory p0(0);\nHistory p1(0);\nHistory p2(0);\nHistory p3(0);\nHistory p4(0);\nHistory p5(0);\nHistory p6(0);\nHistory p7(0);\nHistory p8(0);\nHistory p9(0);\nHistory p10(0);\nHistory p11(0);\nHistory p12(0);\nHistory p13(0);\nHistory p14(0);\nHistory p15(0);\n\nHistory e0(0);\nHistory e1(0);\nHistory e2(0);\nHistory e3(0);\nHistory e4(0);\nHistory e5(0);\nHistory e6(0);\nHistory e7(0);\nHistory e8(0);\nHistory e9(0);\nHistory e10(0);\nHistory e11(0);\nHistory e12(0);\nHistory e13(0);\nHistory e14(0);\nHistory e15(0);\n\nHistory sm0(0);\nHistory sm1(0);\nHistory sm2(0);\nHistory sm3(0);\nHistory sm4(0);\nHistory sm5(0);\nHistory sm6(0);\nHistory sm7(0);\nHistory sm8(0);\nHistory sm9(0);\nHistory sm10(0);\nHistory sm11(0);\nHistory sm12(0);\nHistory sm13(0);\nHistory sm14(0);\nHistory sm15(0);\n\nHistory sph0(0);\nHistory sph1(0);\nHistory sph2(0);\nHistory sph3(0);\nHistory sph4(0);\nHistory sph5(0);\nHistory sph6(0);\nHistory sph7(0);\nHistory sph8(0);\nHistory sph9(0);\nHistory sph10(0);\nHistory sph11(0);\nHistory sph12(0);\nHistory sph13(0);\nHistory sph14(0);\nHistory sph15(0);\n\nfreq = (in1 > 0) * in1 + (in1 <= 0) * default_freq;\npur = clamp(purity, 0, 1);\nent = clamp(entropy, 0, 1);\ncoh = clamp(coherence, 0, 1);\n\nmag_ms = max(magnitude_smooth_ms, 0.1);\nmag_coeff = exp(-1 / (mag_ms * 0.001 * samplerate));\n\ntm0 = clamp(m0, 0, 1);\ntm1 = clamp(m1, 0, 1);\ntm2 = clamp(m2, 0, 1);\ntm3 = clamp(m3, 0, 1);\ntm4 = clamp(m4, 0, 1);\ntm5 = clamp(m5, 0, 1);\ntm6 = clamp(m6, 0, 1);\ntm7 = clamp(m7, 0, 1);\ntm8 = clamp(m8, 0, 1);\ntm9 = clamp(m9, 0, 1);\ntm10 = clamp(m10, 0, 1);\ntm11 = clamp(m11, 0, 1);\ntm12 = clamp(m12, 0, 1);\ntm13 = clamp(m13, 0, 1);\ntm14 = clamp(m14, 0, 1);\ntm15 = clamp(m15, 0, 1);\n\nsm0 = tm0 + mag_coeff * (sm0 - tm0);\nsm1 = tm1 + mag_coeff * (sm1 - tm1);\nsm2 = tm2 + mag_coeff * (sm2 - tm2);\nsm3 = tm3 + mag_coeff * (sm3 - tm3);\nsm4 = tm4 + mag_coeff * (sm4 - tm4);\nsm5 = tm5 + mag_coeff * (sm5 - tm5);\nsm6 = tm6 + mag_coeff * (sm6 - tm6);\nsm7 = tm7 + mag_coeff * (sm7 - tm7);\nsm8 = tm8 + mag_coeff * (sm8 - tm8);\nsm9 = tm9 + mag_coeff * (sm9 - tm9);\nsm10 = tm10 + mag_coeff * (sm10 - tm10);\nsm11 = tm11 + mag_coeff * (sm11 - tm11);\nsm12 = tm12 + mag_coeff * (sm12 - tm12);\nsm13 = tm13 + mag_coeff * (sm13 - tm13);\nsm14 = tm14 + mag_coeff * (sm14 - tm14);\nsm15 = tm15 + mag_coeff * (sm15 - tm15);\n\nphase_ms = max(phase_smooth_ms, 0.1);\nphase_coeff = exp(-1 / (phase_ms * 0.001 * samplerate));\n\ndph0 = atan2(sin(ph0 - sph0), cos(ph0 - sph0));\ndph1 = atan2(sin(ph1 - sph1), cos(ph1 - sph1));\ndph2 = atan2(sin(ph2 - sph2), cos(ph2 - sph2));\ndph3 = atan2(sin(ph3 - sph3), cos(ph3 - sph3));\ndph4 = atan2(sin(ph4 - sph4), cos(ph4 - sph4));\ndph5 = atan2(sin(ph5 - sph5), cos(ph5 - sph5));\ndph6 = atan2(sin(ph6 - sph6), cos(ph6 - sph6));\ndph7 = atan2(sin(ph7 - sph7), cos(ph7 - sph7));\ndph8 = atan2(sin(ph8 - sph8), cos(ph8 - sph8));\ndph9 = atan2(sin(ph9 - sph9), cos(ph9 - sph9));\ndph10 = atan2(sin(ph10 - sph10), cos(ph10 - sph10));\ndph11 = atan2(sin(ph11 - sph11), cos(ph11 - sph11));\ndph12 = atan2(sin(ph12 - sph12), cos(ph12 - sph12));\ndph13 = atan2(sin(ph13 - sph13), cos(ph13 - sph13));\ndph14 = atan2(sin(ph14 - sph14), cos(ph14 - sph14));\ndph15 = atan2(sin(ph15 - sph15), cos(ph15 - sph15));\n\nsph0 = sph0 + (1 - phase_coeff) * dph0;\nsph1 = sph1 + (1 - phase_coeff) * dph1;\nsph2 = sph2 + (1 - phase_coeff) * dph2;\nsph3 = sph3 + (1 - phase_coeff) * dph3;\nsph4 = sph4 + (1 - phase_coeff) * dph4;\nsph5 = sph5 + (1 - phase_coeff) * dph5;\nsph6 = sph6 + (1 - phase_coeff) * dph6;\nsph7 = sph7 + (1 - phase_coeff) * dph7;\nsph8 = sph8 + (1 - phase_coeff) * dph8;\nsph9 = sph9 + (1 - phase_coeff) * dph9;\nsph10 = sph10 + (1 - phase_coeff) * dph10;\nsph11 = sph11 + (1 - phase_coeff) * dph11;\nsph12 = sph12 + (1 - phase_coeff) * dph12;\nsph13 = sph13 + (1 - phase_coeff) * dph13;\nsph14 = sph14 + (1 - phase_coeff) * dph14;\nsph15 = sph15 + (1 - phase_coeff) * dph15;\n\natk_ms = max(attack_ms * mix(1.35, 0.65, coh), 0.1);\natk_coeff = exp(-1 / (atk_ms * 0.001 * samplerate));\n\nspd0 = clamp(abs(s0), 0, 1);\nspd1 = clamp(abs(s1), 0, 1);\nspd2 = clamp(abs(s2), 0, 1);\nspd3 = clamp(abs(s3), 0, 1);\nspd4 = clamp(abs(s4), 0, 1);\nspd5 = clamp(abs(s5), 0, 1);\nspd6 = clamp(abs(s6), 0, 1);\nspd7 = clamp(abs(s7), 0, 1);\nspd8 = clamp(abs(s8), 0, 1);\nspd9 = clamp(abs(s9), 0, 1);\nspd10 = clamp(abs(s10), 0, 1);\nspd11 = clamp(abs(s11), 0, 1);\nspd12 = clamp(abs(s12), 0, 1);\nspd13 = clamp(abs(s13), 0, 1);\nspd14 = clamp(abs(s14), 0, 1);\nspd15 = clamp(abs(s15), 0, 1);\n\ndec0 = mix(slow_decay_ms, fast_decay_ms, spd0);\ndec1 = mix(slow_decay_ms, fast_decay_ms, spd1);\ndec2 = mix(slow_decay_ms, fast_decay_ms, spd2);\ndec3 = mix(slow_decay_ms, fast_decay_ms, spd3);\ndec4 = mix(slow_decay_ms, fast_decay_ms, spd4);\ndec5 = mix(slow_decay_ms, fast_decay_ms, spd5);\ndec6 = mix(slow_decay_ms, fast_decay_ms, spd6);\ndec7 = mix(slow_decay_ms, fast_decay_ms, spd7);\ndec8 = mix(slow_decay_ms, fast_decay_ms, spd8);\ndec9 = mix(slow_decay_ms, fast_decay_ms, spd9);\ndec10 = mix(slow_decay_ms, fast_decay_ms, spd10);\ndec11 = mix(slow_decay_ms, fast_decay_ms, spd11);\ndec12 = mix(slow_decay_ms, fast_decay_ms, spd12);\ndec13 = mix(slow_decay_ms, fast_decay_ms, spd13);\ndec14 = mix(slow_decay_ms, fast_decay_ms, spd14);\ndec15 = mix(slow_decay_ms, fast_decay_ms, spd15);\n\ndc0 = exp(-1 / (max(dec0, 0.1) * 0.001 * samplerate));\ndc1 = exp(-1 / (max(dec1, 0.1) * 0.001 * samplerate));\ndc2 = exp(-1 / (max(dec2, 0.1) * 0.001 * samplerate));\ndc3 = exp(-1 / (max(dec3, 0.1) * 0.001 * samplerate));\ndc4 = exp(-1 / (max(dec4, 0.1) * 0.001 * samplerate));\ndc5 = exp(-1 / (max(dec5, 0.1) * 0.001 * samplerate));\ndc6 = exp(-1 / (max(dec6, 0.1) * 0.001 * samplerate));\ndc7 = exp(-1 / (max(dec7, 0.1) * 0.001 * samplerate));\ndc8 = exp(-1 / (max(dec8, 0.1) * 0.001 * samplerate));\ndc9 = exp(-1 / (max(dec9, 0.1) * 0.001 * samplerate));\ndc10 = exp(-1 / (max(dec10, 0.1) * 0.001 * samplerate));\ndc11 = exp(-1 / (max(dec11, 0.1) * 0.001 * samplerate));\ndc12 = exp(-1 / (max(dec12, 0.1) * 0.001 * samplerate));\ndc13 = exp(-1 / (max(dec13, 0.1) * 0.001 * samplerate));\ndc14 = exp(-1 / (max(dec14, 0.1) * 0.001 * samplerate));\ndc15 = exp(-1 / (max(dec15, 0.1) * 0.001 * samplerate));\n\n// Higher entropy lifts weaker modes. Higher purity makes excitation more selective.\nexc_shape = mix(0.55, 1.6, pur);\nt0 = pow(sm0 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt1 = pow(sm1 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt2 = pow(sm2 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt3 = pow(sm3 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt4 = pow(sm4 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt5 = pow(sm5 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt6 = pow(sm6 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt7 = pow(sm7 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt8 = pow(sm8 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt9 = pow(sm9 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt10 = pow(sm10 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt11 = pow(sm11 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt12 = pow(sm12 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt13 = pow(sm13 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt14 = pow(sm14 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt15 = pow(sm15 + 0.00001, exc_shape) * mix(0.35, 1, ent);\n\ne0 = (t0 > e0) * (t0 + atk_coeff * (e0 - t0)) + (t0 <= e0) * (t0 + dc0 * (e0 - t0));\ne1 = (t1 > e1) * (t1 + atk_coeff * (e1 - t1)) + (t1 <= e1) * (t1 + dc1 * (e1 - t1));\ne2 = (t2 > e2) * (t2 + atk_coeff * (e2 - t2)) + (t2 <= e2) * (t2 + dc2 * (e2 - t2));\ne3 = (t3 > e3) * (t3 + atk_coeff * (e3 - t3)) + (t3 <= e3) * (t3 + dc3 * (e3 - t3));\ne4 = (t4 > e4) * (t4 + atk_coeff * (e4 - t4)) + (t4 <= e4) * (t4 + dc4 * (e4 - t4));\ne5 = (t5 > e5) * (t5 + atk_coeff * (e5 - t5)) + (t5 <= e5) * (t5 + dc5 * (e5 - t5));\ne6 = (t6 > e6) * (t6 + atk_coeff * (e6 - t6)) + (t6 <= e6) * (t6 + dc6 * (e6 - t6));\ne7 = (t7 > e7) * (t7 + atk_coeff * (e7 - t7)) + (t7 <= e7) * (t7 + dc7 * (e7 - t7));\ne8 = (t8 > e8) * (t8 + atk_coeff * (e8 - t8)) + (t8 <= e8) * (t8 + dc8 * (e8 - t8));\ne9 = (t9 > e9) * (t9 + atk_coeff * (e9 - t9)) + (t9 <= e9) * (t9 + dc9 * (e9 - t9));\ne10 = (t10 > e10) * (t10 + atk_coeff * (e10 - t10)) + (t10 <= e10) * (t10 + dc10 * (e10 - t10));\ne11 = (t11 > e11) * (t11 + atk_coeff * (e11 - t11)) + (t11 <= e11) * (t11 + dc11 * (e11 - t11));\ne12 = (t12 > e12) * (t12 + atk_coeff * (e12 - t12)) + (t12 <= e12) * (t12 + dc12 * (e12 - t12));\ne13 = (t13 > e13) * (t13 + atk_coeff * (e13 - t13)) + (t13 <= e13) * (t13 + dc13 * (e13 - t13));\ne14 = (t14 > e14) * (t14 + atk_coeff * (e14 - t14)) + (t14 <= e14) * (t14 + dc14 * (e14 - t14));\ne15 = (t15 > e15) * (t15 + atk_coeff * (e15 - t15)) + (t15 <= e15) * (t15 + dc15 * (e15 - t15));\n\nbright = clamp(brightness + ent * 0.25, 0, 1);\n\np0 = fract(p0 + freq * max(h0, 0.01) / samplerate);\np1 = fract(p1 + freq * max(h1, 0.01) / samplerate);\np2 = fract(p2 + freq * max(h2, 0.01) / samplerate);\np3 = fract(p3 + freq * max(h3, 0.01) / samplerate);\np4 = fract(p4 + freq * max(h4, 0.01) / samplerate);\np5 = fract(p5 + freq * max(h5, 0.01) / samplerate);\np6 = fract(p6 + freq * max(h6, 0.01) / samplerate);\np7 = fract(p7 + freq * max(h7, 0.01) / samplerate);\np8 = fract(p8 + freq * max(h8, 0.01) / samplerate);\np9 = fract(p9 + freq * max(h9, 0.01) / samplerate);\np10 = fract(p10 + freq * max(h10, 0.01) / samplerate);\np11 = fract(p11 + freq * max(h11, 0.01) / samplerate);\np12 = fract(p12 + freq * max(h12, 0.01) / samplerate);\np13 = fract(p13 + freq * max(h13, 0.01) / samplerate);\np14 = fract(p14 + freq * max(h14, 0.01) / samplerate);\np15 = fract(p15 + freq * max(h15, 0.01) / samplerate);\n\ntwopi = 6.283185307179586;\npartials =\n    e0 * sin(twopi * p0 + sph0) / pow(max(h0, 1), bright) +\n    e1 * sin(twopi * p1 + sph1) / pow(max(h1, 1), bright) +\n    e2 * sin(twopi * p2 + sph2) / pow(max(h2, 1), bright) +\n    e3 * sin(twopi * p3 + sph3) / pow(max(h3, 1), bright) +\n    e4 * sin(twopi * p4 + sph4) / pow(max(h4, 1), bright) +\n    e5 * sin(twopi * p5 + sph5) / pow(max(h5, 1), bright) +\n    e6 * sin(twopi * p6 + sph6) / pow(max(h6, 1), bright) +\n    e7 * sin(twopi * p7 + sph7) / pow(max(h7, 1), bright) +\n    e8 * sin(twopi * p8 + sph8) / pow(max(h8, 1), bright) +\n    e9 * sin(twopi * p9 + sph9) / pow(max(h9, 1), bright) +\n    e10 * sin(twopi * p10 + sph10) / pow(max(h10, 1), bright) +\n    e11 * sin(twopi * p11 + sph11) / pow(max(h11, 1), bright) +\n    e12 * sin(twopi * p12 + sph12) / pow(max(h12, 1), bright) +\n    e13 * sin(twopi * p13 + sph13) / pow(max(h13, 1), bright) +\n    e14 * sin(twopi * p14 + sph14) / pow(max(h14, 1), bright) +\n    e15 * sin(twopi * p15 + sph15) / pow(max(h15, 1), bright);\n\nvoice_scale = 1 / sqrt(max(mix_voices, 1));\nsig = partials;\n\nout1 = sig * amp * output_ceiling * voice_scale;\nout2 = e0 + e1 + e2 + e3 + e4 + e5 + e6 + e7 + e8 + e9 + e10 + e11 + e12 + e13 + e14 + e15;\nout3 = freq;\n",
					"fontface" : 0,
					"fontname" : "<Monospaced>",
					"fontsize" : 12.0,
					"id" : "obj-13",
					"maxclass" : "gen.codebox~",
					"numinlets" : 1,
					"numoutlets" : 3,
					"outlettype" : [ "signal", "signal", "signal" ],
					"patching_rect" : [ 39.0, 391.5, 126.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-12",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 346.0, 171.0, 111.0, 22.0 ],
					"text" : "prepend harmonics"
				}

			}
, 			{
				"box" : 				{
					"automatic" : 1,
					"id" : "obj-49",
					"maxclass" : "scope~",
					"numinlets" : 2,
					"numoutlets" : 0,
					"patching_rect" : [ 497.0, 526.0, 130.0, 130.0 ]
				}

			}
, 			{
				"box" : 				{
					"automatic" : 1,
					"id" : "obj-48",
					"maxclass" : "scope~",
					"numinlets" : 2,
					"numoutlets" : 0,
					"patching_rect" : [ 359.0, 526.0, 130.0, 130.0 ]
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "obj-40",
					"maxclass" : "flonum",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 619.0, 469.0, 50.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-41",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 473.0, 442.0, 34.0, 22.0 ],
					"text" : "*~ 1."
				}

			}
, 			{
				"box" : 				{
					"automatic" : 1,
					"id" : "obj-38",
					"maxclass" : "scope~",
					"numinlets" : 2,
					"numoutlets" : 0,
					"patching_rect" : [ 222.0, 526.0, 130.0, 130.0 ]
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "obj-30",
					"maxclass" : "flonum",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 328.0, 447.0, 50.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-32",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 222.0, 474.0, 34.0, 22.0 ],
					"text" : "*~ 1."
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-15",
					"linecount" : 9,
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 681.333353638648987, -5.66667914390564, 150.0, 127.0 ],
					"text" : "amp 0.2\nattack_ms 12\nslow_decay_ms 900\nfast_decay_ms 70\nmagnitude_smooth_ms 100\nphase_smooth_ms 100\nbrightness 0.65\nmix_voices 4"
				}

			}
, 			{
				"box" : 				{
					"automatic" : 1,
					"id" : "obj-11",
					"maxclass" : "scope~",
					"numinlets" : 2,
					"numoutlets" : 0,
					"patching_rect" : [ 76.5, 526.0, 130.0, 130.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-10",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 248.0, 171.0, 89.0, 22.0 ],
					"text" : "prepend phase"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-8",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 154.0, 171.0, 89.0, 22.0 ],
					"text" : "prepend speed"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-5",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 0.0, 177.0, 112.0, 22.0 ],
					"text" : "prepend magnitude"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-74",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 39.0, 333.0, 31.0, 22.0 ],
					"text" : "sig~"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "obj-75",
					"maxclass" : "flonum",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 39.0, 306.0, 50.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-61",
					"maxclass" : "newobj",
					"numinlets" : 4,
					"numoutlets" : 4,
					"outlettype" : [ "", "", "", "" ],
					"patching_rect" : [ 39.0, 219.0, 205.0, 22.0 ],
					"saved_object_attributes" : 					{
						"filename" : "qmw_density_field_to_resonator.js",
						"parameter_enable" : 0
					}
,
					"text" : "js qmw_density_field_to_resonator.js"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "obj-59",
					"maxclass" : "flonum",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 82.0, 455.0, 50.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-57",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 36.0, 498.0, 34.0, 22.0 ],
					"text" : "*~ 1."
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-44",
					"maxclass" : "ezdac~",
					"numinlets" : 2,
					"numoutlets" : 0,
					"patching_rect" : [ 794.0, 611.0, 45.0, 45.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-4",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 277.333341598510742, 12.000000357627869, 97.0, 22.0 ],
					"text" : "udpreceive 7400"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-3",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "" ],
					"patching_rect" : [ 277.333341598510742, 42.666667938232422, 98.0, 22.0 ],
					"text" : "OSC-route /qmw"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-2",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "" ],
					"patching_rect" : [ 277.333341598510742, 80.000002384185791, 139.0, 22.0 ],
					"text" : "OSC-route /density_field"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-1",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 8,
					"outlettype" : [ "", "", "", "", "", "", "", "" ],
					"patching_rect" : [ 213.333339691162109, 114.333324432373047, 415.0, 22.0 ],
					"text" : "OSC-route /speed /magnitude /phase /harmonics /entropy /purity /coherence"
				}

			}
 ],
		"lines" : [ 			{
				"patchline" : 				{
					"destination" : [ "obj-10", 0 ],
					"source" : [ "obj-1", 3 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-12", 0 ],
					"order" : 1,
					"source" : [ "obj-1", 4 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-36", 1 ],
					"order" : 0,
					"source" : [ "obj-1", 6 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-45", 0 ],
					"order" : 0,
					"source" : [ "obj-1", 5 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-5", 0 ],
					"source" : [ "obj-1", 2 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-50", 1 ],
					"order" : 0,
					"source" : [ "obj-1", 4 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-6", 0 ],
					"order" : 1,
					"source" : [ "obj-1", 5 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-7", 0 ],
					"order" : 1,
					"source" : [ "obj-1", 6 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-8", 0 ],
					"source" : [ "obj-1", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-61", 1 ],
					"source" : [ "obj-10", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-101", 0 ],
					"source" : [ "obj-100", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-17", 0 ],
					"hidden" : 1,
					"source" : [ "obj-101", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-103", 0 ],
					"source" : [ "obj-102", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-108", 0 ],
					"source" : [ "obj-106", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-106", 0 ],
					"source" : [ "obj-107", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-112", 0 ],
					"source" : [ "obj-108", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-108", 0 ],
					"source" : [ "obj-109", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-109", 0 ],
					"source" : [ "obj-110", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-112", 1 ],
					"source" : [ "obj-111", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-17", 1 ],
					"order" : 0,
					"source" : [ "obj-112", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-49", 0 ],
					"order" : 1,
					"source" : [ "obj-112", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-61", 3 ],
					"source" : [ "obj-12", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-57", 0 ],
					"source" : [ "obj-13", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-13", 0 ],
					"source" : [ "obj-14", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-14", 0 ],
					"source" : [ "obj-16", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-44", 1 ],
					"source" : [ "obj-17", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-44", 0 ],
					"source" : [ "obj-17", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-17", 0 ],
					"hidden" : 1,
					"source" : [ "obj-18", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-1", 0 ],
					"source" : [ "obj-2", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-39", 0 ],
					"source" : [ "obj-21", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-21", 0 ],
					"source" : [ "obj-22", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-2", 0 ],
					"source" : [ "obj-3", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-32", 1 ],
					"source" : [ "obj-30", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-17", 1 ],
					"order" : 0,
					"source" : [ "obj-32", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-23", 0 ],
					"order" : 1,
					"source" : [ "obj-32", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-38", 0 ],
					"order" : 2,
					"source" : [ "obj-32", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-17", 0 ],
					"source" : [ "obj-37", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-32", 0 ],
					"source" : [ "obj-39", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-3", 0 ],
					"source" : [ "obj-4", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-41", 1 ],
					"source" : [ "obj-40", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-17", 0 ],
					"order" : 0,
					"source" : [ "obj-41", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-25", 0 ],
					"order" : 1,
					"source" : [ "obj-41", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-48", 0 ],
					"order" : 2,
					"source" : [ "obj-41", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-39", 0 ],
					"source" : [ "obj-42", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-61", 0 ],
					"source" : [ "obj-5", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-11", 0 ],
					"order" : 2,
					"source" : [ "obj-57", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-17", 0 ],
					"order" : 0,
					"source" : [ "obj-57", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-20", 0 ],
					"order" : 1,
					"source" : [ "obj-57", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-42", 0 ],
					"source" : [ "obj-58", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-57", 1 ],
					"source" : [ "obj-59", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-108", 0 ],
					"order" : 0,
					"source" : [ "obj-6", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-13", 0 ],
					"order" : 3,
					"source" : [ "obj-6", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-39", 0 ],
					"order" : 2,
					"source" : [ "obj-6", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-63", 0 ],
					"order" : 1,
					"source" : [ "obj-6", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-63", 0 ],
					"source" : [ "obj-60", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-108", 0 ],
					"source" : [ "obj-61", 3 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-13", 0 ],
					"source" : [ "obj-61", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-39", 0 ],
					"source" : [ "obj-61", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-63", 0 ],
					"source" : [ "obj-61", 2 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-60", 0 ],
					"source" : [ "obj-62", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-41", 0 ],
					"source" : [ "obj-63", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-63", 0 ],
					"source" : [ "obj-64", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-64", 0 ],
					"source" : [ "obj-65", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-108", 0 ],
					"order" : 0,
					"source" : [ "obj-7", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-13", 0 ],
					"order" : 3,
					"source" : [ "obj-7", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-39", 0 ],
					"order" : 2,
					"source" : [ "obj-7", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-63", 0 ],
					"order" : 1,
					"source" : [ "obj-7", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-71", 0 ],
					"source" : [ "obj-70", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-108", 0 ],
					"order" : 0,
					"source" : [ "obj-71", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-13", 0 ],
					"order" : 3,
					"source" : [ "obj-71", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-39", 0 ],
					"order" : 2,
					"source" : [ "obj-71", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-63", 0 ],
					"order" : 1,
					"source" : [ "obj-71", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-13", 0 ],
					"source" : [ "obj-74", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-74", 0 ],
					"source" : [ "obj-75", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-61", 2 ],
					"source" : [ "obj-8", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-85", 0 ],
					"source" : [ "obj-84", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-17", 0 ],
					"hidden" : 1,
					"source" : [ "obj-85", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-37", 0 ],
					"source" : [ "obj-86", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-89", 1 ],
					"source" : [ "obj-87", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-89", 0 ],
					"source" : [ "obj-88", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-90", 0 ],
					"source" : [ "obj-89", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-17", 0 ],
					"source" : [ "obj-90", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-92", 0 ],
					"source" : [ "obj-91", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-17", 0 ],
					"hidden" : 1,
					"source" : [ "obj-92", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-99", 0 ],
					"source" : [ "obj-93", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-18", 0 ],
					"source" : [ "obj-94", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-96", 0 ],
					"source" : [ "obj-95", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-17", 0 ],
					"source" : [ "obj-96", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-98", 0 ],
					"source" : [ "obj-97", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-17", 0 ],
					"hidden" : 1,
					"source" : [ "obj-98", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-17", 0 ],
					"hidden" : 1,
					"source" : [ "obj-99", 0 ]
				}

			}
 ],
		"originid" : "pat-860",
		"dependency_cache" : [ 			{
				"name" : "OSC-route.mxo",
				"type" : "iLaX"
			}
, 			{
				"name" : "qmw_density_field_to_resonator.js",
				"bootpath" : "~/QuantumSonification/max/patches/QMW_Music_of_the_Spheres_Resonator_v1",
				"patcherrelativepath" : ".",
				"type" : "TEXT",
				"implicit" : 1
			}
, 			{
				"name" : "spat5.converb~.mxo",
				"type" : "iLaX"
			}
, 			{
				"name" : "vb.mi.verb~.mxo",
				"type" : "iLaX"
			}
 ],
		"autosave" : 0
	}

}
