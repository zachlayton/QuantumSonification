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
		"rect" : [ 42.0, 108.0, 1266.0, 800.0 ],
		"gridsize" : [ 15.0, 15.0 ],
		"boxes" : [ 			{
				"box" : 				{
					"id" : "obj-53",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1368.000040769577026, 524.000015616416931, 79.0, 22.0 ],
					"text" : "prepend amp"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "obj-54",
					"maxclass" : "flonum",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 1361.33337390422821, 464.000013828277588, 50.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-55",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 1288.000038385391235, 522.666682243347168, 31.0, 22.0 ],
					"text" : "sig~"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "obj-56",
					"maxclass" : "flonum",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 1285.333371639251709, 480.000014305114746, 50.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"automatic" : 1,
					"id" : "obj-49",
					"maxclass" : "scope~",
					"numinlets" : 2,
					"numoutlets" : 0,
					"patching_rect" : [ 1033.333364129066467, 745.33335554599762, 130.0, 130.0 ]
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "obj-50",
					"maxclass" : "flonum",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 1182.666701912879944, 637.333352327346802, 50.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-51",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 1144.666670083999634, 673.333353400230408, 34.0, 22.0 ],
					"text" : "*~ 1."
				}

			}
, 			{
				"box" : 				{
					"code" : "// QMW Density Field Quantum Resonator 16\n//\n// Gen~ codebox.\n// in1 is the carrier frequency in Hz.\n// m0..m15 excite sixteen resonant partials.\n// ph0..ph15 set smoothed per-partial timing/phase.\n// s0..s15 set lifetime: fast lanes flash, slow lanes ring.\n// h0..h15 are partial ratios. Defaults are harmonic 1..16, but these can\n// later be replaced by Hamiltonian energy-gap ratios.\n\nParam m0(0);\nParam m1(0);\nParam m2(0);\nParam m3(0);\nParam m4(0);\nParam m5(0);\nParam m6(0);\nParam m7(0);\nParam m8(0);\nParam m9(0);\nParam m10(0);\nParam m11(0);\nParam m12(0);\nParam m13(0);\nParam m14(0);\nParam m15(0);\n\nParam ph0(0);\nParam ph1(0);\nParam ph2(0);\nParam ph3(0);\nParam ph4(0);\nParam ph5(0);\nParam ph6(0);\nParam ph7(0);\nParam ph8(0);\nParam ph9(0);\nParam ph10(0);\nParam ph11(0);\nParam ph12(0);\nParam ph13(0);\nParam ph14(0);\nParam ph15(0);\n\nParam s0(0);\nParam s1(0);\nParam s2(0);\nParam s3(0);\nParam s4(0);\nParam s5(0);\nParam s6(0);\nParam s7(0);\nParam s8(0);\nParam s9(0);\nParam s10(0);\nParam s11(0);\nParam s12(0);\nParam s13(0);\nParam s14(0);\nParam s15(0);\n\nParam h0(1);\nParam h1(2);\nParam h2(3);\nParam h3(4);\nParam h4(5);\nParam h5(6);\nParam h6(7);\nParam h7(8);\nParam h8(9);\nParam h9(10);\nParam h10(11);\nParam h11(12);\nParam h12(13);\nParam h13(14);\nParam h14(15);\nParam h15(16);\n\nParam purity(1);\nParam entropy(0);\nParam coherence(0);\nParam amp(0.2);\nParam default_freq(55);\nParam attack_ms(12);\nParam slow_decay_ms(900);\nParam fast_decay_ms(70);\nParam phase_smooth_ms(100);\nParam magnitude_smooth_ms(100);\nParam brightness(0.65);\nParam mix_voices(4);\nParam output_ceiling(0.85);\n\nHistory p0(0);\nHistory p1(0);\nHistory p2(0);\nHistory p3(0);\nHistory p4(0);\nHistory p5(0);\nHistory p6(0);\nHistory p7(0);\nHistory p8(0);\nHistory p9(0);\nHistory p10(0);\nHistory p11(0);\nHistory p12(0);\nHistory p13(0);\nHistory p14(0);\nHistory p15(0);\n\nHistory e0(0);\nHistory e1(0);\nHistory e2(0);\nHistory e3(0);\nHistory e4(0);\nHistory e5(0);\nHistory e6(0);\nHistory e7(0);\nHistory e8(0);\nHistory e9(0);\nHistory e10(0);\nHistory e11(0);\nHistory e12(0);\nHistory e13(0);\nHistory e14(0);\nHistory e15(0);\n\nHistory sm0(0);\nHistory sm1(0);\nHistory sm2(0);\nHistory sm3(0);\nHistory sm4(0);\nHistory sm5(0);\nHistory sm6(0);\nHistory sm7(0);\nHistory sm8(0);\nHistory sm9(0);\nHistory sm10(0);\nHistory sm11(0);\nHistory sm12(0);\nHistory sm13(0);\nHistory sm14(0);\nHistory sm15(0);\n\nHistory sph0(0);\nHistory sph1(0);\nHistory sph2(0);\nHistory sph3(0);\nHistory sph4(0);\nHistory sph5(0);\nHistory sph6(0);\nHistory sph7(0);\nHistory sph8(0);\nHistory sph9(0);\nHistory sph10(0);\nHistory sph11(0);\nHistory sph12(0);\nHistory sph13(0);\nHistory sph14(0);\nHistory sph15(0);\n\nfreq = (in1 > 0) * in1 + (in1 <= 0) * default_freq;\npur = clamp(purity, 0, 1);\nent = clamp(entropy, 0, 1);\ncoh = clamp(coherence, 0, 1);\n\nmag_ms = max(magnitude_smooth_ms, 0.1);\nmag_coeff = exp(-1 / (mag_ms * 0.001 * samplerate));\n\ntm0 = clamp(m0, 0, 1);\ntm1 = clamp(m1, 0, 1);\ntm2 = clamp(m2, 0, 1);\ntm3 = clamp(m3, 0, 1);\ntm4 = clamp(m4, 0, 1);\ntm5 = clamp(m5, 0, 1);\ntm6 = clamp(m6, 0, 1);\ntm7 = clamp(m7, 0, 1);\ntm8 = clamp(m8, 0, 1);\ntm9 = clamp(m9, 0, 1);\ntm10 = clamp(m10, 0, 1);\ntm11 = clamp(m11, 0, 1);\ntm12 = clamp(m12, 0, 1);\ntm13 = clamp(m13, 0, 1);\ntm14 = clamp(m14, 0, 1);\ntm15 = clamp(m15, 0, 1);\n\nsm0 = tm0 + mag_coeff * (sm0 - tm0);\nsm1 = tm1 + mag_coeff * (sm1 - tm1);\nsm2 = tm2 + mag_coeff * (sm2 - tm2);\nsm3 = tm3 + mag_coeff * (sm3 - tm3);\nsm4 = tm4 + mag_coeff * (sm4 - tm4);\nsm5 = tm5 + mag_coeff * (sm5 - tm5);\nsm6 = tm6 + mag_coeff * (sm6 - tm6);\nsm7 = tm7 + mag_coeff * (sm7 - tm7);\nsm8 = tm8 + mag_coeff * (sm8 - tm8);\nsm9 = tm9 + mag_coeff * (sm9 - tm9);\nsm10 = tm10 + mag_coeff * (sm10 - tm10);\nsm11 = tm11 + mag_coeff * (sm11 - tm11);\nsm12 = tm12 + mag_coeff * (sm12 - tm12);\nsm13 = tm13 + mag_coeff * (sm13 - tm13);\nsm14 = tm14 + mag_coeff * (sm14 - tm14);\nsm15 = tm15 + mag_coeff * (sm15 - tm15);\n\nphase_ms = max(phase_smooth_ms, 0.1);\nphase_coeff = exp(-1 / (phase_ms * 0.001 * samplerate));\n\ndph0 = atan2(sin(ph0 - sph0), cos(ph0 - sph0));\ndph1 = atan2(sin(ph1 - sph1), cos(ph1 - sph1));\ndph2 = atan2(sin(ph2 - sph2), cos(ph2 - sph2));\ndph3 = atan2(sin(ph3 - sph3), cos(ph3 - sph3));\ndph4 = atan2(sin(ph4 - sph4), cos(ph4 - sph4));\ndph5 = atan2(sin(ph5 - sph5), cos(ph5 - sph5));\ndph6 = atan2(sin(ph6 - sph6), cos(ph6 - sph6));\ndph7 = atan2(sin(ph7 - sph7), cos(ph7 - sph7));\ndph8 = atan2(sin(ph8 - sph8), cos(ph8 - sph8));\ndph9 = atan2(sin(ph9 - sph9), cos(ph9 - sph9));\ndph10 = atan2(sin(ph10 - sph10), cos(ph10 - sph10));\ndph11 = atan2(sin(ph11 - sph11), cos(ph11 - sph11));\ndph12 = atan2(sin(ph12 - sph12), cos(ph12 - sph12));\ndph13 = atan2(sin(ph13 - sph13), cos(ph13 - sph13));\ndph14 = atan2(sin(ph14 - sph14), cos(ph14 - sph14));\ndph15 = atan2(sin(ph15 - sph15), cos(ph15 - sph15));\n\nsph0 = sph0 + (1 - phase_coeff) * dph0;\nsph1 = sph1 + (1 - phase_coeff) * dph1;\nsph2 = sph2 + (1 - phase_coeff) * dph2;\nsph3 = sph3 + (1 - phase_coeff) * dph3;\nsph4 = sph4 + (1 - phase_coeff) * dph4;\nsph5 = sph5 + (1 - phase_coeff) * dph5;\nsph6 = sph6 + (1 - phase_coeff) * dph6;\nsph7 = sph7 + (1 - phase_coeff) * dph7;\nsph8 = sph8 + (1 - phase_coeff) * dph8;\nsph9 = sph9 + (1 - phase_coeff) * dph9;\nsph10 = sph10 + (1 - phase_coeff) * dph10;\nsph11 = sph11 + (1 - phase_coeff) * dph11;\nsph12 = sph12 + (1 - phase_coeff) * dph12;\nsph13 = sph13 + (1 - phase_coeff) * dph13;\nsph14 = sph14 + (1 - phase_coeff) * dph14;\nsph15 = sph15 + (1 - phase_coeff) * dph15;\n\natk_ms = max(attack_ms * mix(1.35, 0.65, coh), 0.1);\natk_coeff = exp(-1 / (atk_ms * 0.001 * samplerate));\n\nspd0 = clamp(abs(s0), 0, 1);\nspd1 = clamp(abs(s1), 0, 1);\nspd2 = clamp(abs(s2), 0, 1);\nspd3 = clamp(abs(s3), 0, 1);\nspd4 = clamp(abs(s4), 0, 1);\nspd5 = clamp(abs(s5), 0, 1);\nspd6 = clamp(abs(s6), 0, 1);\nspd7 = clamp(abs(s7), 0, 1);\nspd8 = clamp(abs(s8), 0, 1);\nspd9 = clamp(abs(s9), 0, 1);\nspd10 = clamp(abs(s10), 0, 1);\nspd11 = clamp(abs(s11), 0, 1);\nspd12 = clamp(abs(s12), 0, 1);\nspd13 = clamp(abs(s13), 0, 1);\nspd14 = clamp(abs(s14), 0, 1);\nspd15 = clamp(abs(s15), 0, 1);\n\ndec0 = mix(slow_decay_ms, fast_decay_ms, spd0);\ndec1 = mix(slow_decay_ms, fast_decay_ms, spd1);\ndec2 = mix(slow_decay_ms, fast_decay_ms, spd2);\ndec3 = mix(slow_decay_ms, fast_decay_ms, spd3);\ndec4 = mix(slow_decay_ms, fast_decay_ms, spd4);\ndec5 = mix(slow_decay_ms, fast_decay_ms, spd5);\ndec6 = mix(slow_decay_ms, fast_decay_ms, spd6);\ndec7 = mix(slow_decay_ms, fast_decay_ms, spd7);\ndec8 = mix(slow_decay_ms, fast_decay_ms, spd8);\ndec9 = mix(slow_decay_ms, fast_decay_ms, spd9);\ndec10 = mix(slow_decay_ms, fast_decay_ms, spd10);\ndec11 = mix(slow_decay_ms, fast_decay_ms, spd11);\ndec12 = mix(slow_decay_ms, fast_decay_ms, spd12);\ndec13 = mix(slow_decay_ms, fast_decay_ms, spd13);\ndec14 = mix(slow_decay_ms, fast_decay_ms, spd14);\ndec15 = mix(slow_decay_ms, fast_decay_ms, spd15);\n\ndc0 = exp(-1 / (max(dec0, 0.1) * 0.001 * samplerate));\ndc1 = exp(-1 / (max(dec1, 0.1) * 0.001 * samplerate));\ndc2 = exp(-1 / (max(dec2, 0.1) * 0.001 * samplerate));\ndc3 = exp(-1 / (max(dec3, 0.1) * 0.001 * samplerate));\ndc4 = exp(-1 / (max(dec4, 0.1) * 0.001 * samplerate));\ndc5 = exp(-1 / (max(dec5, 0.1) * 0.001 * samplerate));\ndc6 = exp(-1 / (max(dec6, 0.1) * 0.001 * samplerate));\ndc7 = exp(-1 / (max(dec7, 0.1) * 0.001 * samplerate));\ndc8 = exp(-1 / (max(dec8, 0.1) * 0.001 * samplerate));\ndc9 = exp(-1 / (max(dec9, 0.1) * 0.001 * samplerate));\ndc10 = exp(-1 / (max(dec10, 0.1) * 0.001 * samplerate));\ndc11 = exp(-1 / (max(dec11, 0.1) * 0.001 * samplerate));\ndc12 = exp(-1 / (max(dec12, 0.1) * 0.001 * samplerate));\ndc13 = exp(-1 / (max(dec13, 0.1) * 0.001 * samplerate));\ndc14 = exp(-1 / (max(dec14, 0.1) * 0.001 * samplerate));\ndc15 = exp(-1 / (max(dec15, 0.1) * 0.001 * samplerate));\n\n// Higher entropy lifts weaker modes. Higher purity makes excitation more selective.\nexc_shape = mix(0.55, 1.6, pur);\nt0 = pow(sm0 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt1 = pow(sm1 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt2 = pow(sm2 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt3 = pow(sm3 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt4 = pow(sm4 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt5 = pow(sm5 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt6 = pow(sm6 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt7 = pow(sm7 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt8 = pow(sm8 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt9 = pow(sm9 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt10 = pow(sm10 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt11 = pow(sm11 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt12 = pow(sm12 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt13 = pow(sm13 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt14 = pow(sm14 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt15 = pow(sm15 + 0.00001, exc_shape) * mix(0.35, 1, ent);\n\ne0 = (t0 > e0) * (t0 + atk_coeff * (e0 - t0)) + (t0 <= e0) * (t0 + dc0 * (e0 - t0));\ne1 = (t1 > e1) * (t1 + atk_coeff * (e1 - t1)) + (t1 <= e1) * (t1 + dc1 * (e1 - t1));\ne2 = (t2 > e2) * (t2 + atk_coeff * (e2 - t2)) + (t2 <= e2) * (t2 + dc2 * (e2 - t2));\ne3 = (t3 > e3) * (t3 + atk_coeff * (e3 - t3)) + (t3 <= e3) * (t3 + dc3 * (e3 - t3));\ne4 = (t4 > e4) * (t4 + atk_coeff * (e4 - t4)) + (t4 <= e4) * (t4 + dc4 * (e4 - t4));\ne5 = (t5 > e5) * (t5 + atk_coeff * (e5 - t5)) + (t5 <= e5) * (t5 + dc5 * (e5 - t5));\ne6 = (t6 > e6) * (t6 + atk_coeff * (e6 - t6)) + (t6 <= e6) * (t6 + dc6 * (e6 - t6));\ne7 = (t7 > e7) * (t7 + atk_coeff * (e7 - t7)) + (t7 <= e7) * (t7 + dc7 * (e7 - t7));\ne8 = (t8 > e8) * (t8 + atk_coeff * (e8 - t8)) + (t8 <= e8) * (t8 + dc8 * (e8 - t8));\ne9 = (t9 > e9) * (t9 + atk_coeff * (e9 - t9)) + (t9 <= e9) * (t9 + dc9 * (e9 - t9));\ne10 = (t10 > e10) * (t10 + atk_coeff * (e10 - t10)) + (t10 <= e10) * (t10 + dc10 * (e10 - t10));\ne11 = (t11 > e11) * (t11 + atk_coeff * (e11 - t11)) + (t11 <= e11) * (t11 + dc11 * (e11 - t11));\ne12 = (t12 > e12) * (t12 + atk_coeff * (e12 - t12)) + (t12 <= e12) * (t12 + dc12 * (e12 - t12));\ne13 = (t13 > e13) * (t13 + atk_coeff * (e13 - t13)) + (t13 <= e13) * (t13 + dc13 * (e13 - t13));\ne14 = (t14 > e14) * (t14 + atk_coeff * (e14 - t14)) + (t14 <= e14) * (t14 + dc14 * (e14 - t14));\ne15 = (t15 > e15) * (t15 + atk_coeff * (e15 - t15)) + (t15 <= e15) * (t15 + dc15 * (e15 - t15));\n\nbright = clamp(brightness + ent * 0.25, 0, 1);\n\np0 = fract(p0 + freq * max(h0, 0.01) / samplerate);\np1 = fract(p1 + freq * max(h1, 0.01) / samplerate);\np2 = fract(p2 + freq * max(h2, 0.01) / samplerate);\np3 = fract(p3 + freq * max(h3, 0.01) / samplerate);\np4 = fract(p4 + freq * max(h4, 0.01) / samplerate);\np5 = fract(p5 + freq * max(h5, 0.01) / samplerate);\np6 = fract(p6 + freq * max(h6, 0.01) / samplerate);\np7 = fract(p7 + freq * max(h7, 0.01) / samplerate);\np8 = fract(p8 + freq * max(h8, 0.01) / samplerate);\np9 = fract(p9 + freq * max(h9, 0.01) / samplerate);\np10 = fract(p10 + freq * max(h10, 0.01) / samplerate);\np11 = fract(p11 + freq * max(h11, 0.01) / samplerate);\np12 = fract(p12 + freq * max(h12, 0.01) / samplerate);\np13 = fract(p13 + freq * max(h13, 0.01) / samplerate);\np14 = fract(p14 + freq * max(h14, 0.01) / samplerate);\np15 = fract(p15 + freq * max(h15, 0.01) / samplerate);\n\ntwopi = 6.283185307179586;\npartials =\n    e0 * sin(twopi * p0 + sph0) / pow(max(h0, 1), bright) +\n    e1 * sin(twopi * p1 + sph1) / pow(max(h1, 1), bright) +\n    e2 * sin(twopi * p2 + sph2) / pow(max(h2, 1), bright) +\n    e3 * sin(twopi * p3 + sph3) / pow(max(h3, 1), bright) +\n    e4 * sin(twopi * p4 + sph4) / pow(max(h4, 1), bright) +\n    e5 * sin(twopi * p5 + sph5) / pow(max(h5, 1), bright) +\n    e6 * sin(twopi * p6 + sph6) / pow(max(h6, 1), bright) +\n    e7 * sin(twopi * p7 + sph7) / pow(max(h7, 1), bright) +\n    e8 * sin(twopi * p8 + sph8) / pow(max(h8, 1), bright) +\n    e9 * sin(twopi * p9 + sph9) / pow(max(h9, 1), bright) +\n    e10 * sin(twopi * p10 + sph10) / pow(max(h10, 1), bright) +\n    e11 * sin(twopi * p11 + sph11) / pow(max(h11, 1), bright) +\n    e12 * sin(twopi * p12 + sph12) / pow(max(h12, 1), bright) +\n    e13 * sin(twopi * p13 + sph13) / pow(max(h13, 1), bright) +\n    e14 * sin(twopi * p14 + sph14) / pow(max(h14, 1), bright) +\n    e15 * sin(twopi * p15 + sph15) / pow(max(h15, 1), bright);\n\nvoice_scale = 1 / sqrt(max(mix_voices, 1));\nsig = tanh(partials * 0.5);\n\nout1 = sig * amp * output_ceiling * voice_scale;\nout2 = e0 + e1 + e2 + e3 + e4 + e5 + e6 + e7 + e8 + e9 + e10 + e11 + e12 + e13 + e14 + e15;\nout3 = freq;\n",
					"fontface" : 0,
					"fontname" : "<Monospaced>",
					"fontsize" : 12.0,
					"id" : "obj-52",
					"maxclass" : "gen.codebox~",
					"numinlets" : 1,
					"numoutlets" : 3,
					"outlettype" : [ "signal", "signal", "signal" ],
					"patching_rect" : [ 802.500023245811462, 490.666681289672852, 88.00000262260437, 42.666667938232422 ]
				}

			}
, 			{
				"box" : 				{
					"automatic" : 1,
					"id" : "obj-48",
					"maxclass" : "scope~",
					"numinlets" : 2,
					"numoutlets" : 0,
					"patching_rect" : [ 885.333359718322754, 749.333355665206909, 130.0, 130.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-46",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1405.333375215530396, 390.000001788139343, 79.0, 22.0 ],
					"text" : "prepend amp"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "obj-47",
					"maxclass" : "flonum",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 1398.66670835018158, 330.0, 50.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-43",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 1325.333372831344604, 388.000011563301086, 31.0, 22.0 ],
					"text" : "sig~"
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
					"patching_rect" : [ 1322.666706085205078, 345.333343625068665, 50.0, 22.0 ]
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
					"patching_rect" : [ 978.666695833206177, 642.666685819625854, 50.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-41",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 872.000025987625122, 669.333353281021118, 34.0, 22.0 ],
					"text" : "*~ 1."
				}

			}
, 			{
				"box" : 				{
					"code" : "// QMW Density Field Quantum Resonator 16\n//\n// Gen~ codebox.\n// in1 is the carrier frequency in Hz.\n// m0..m15 excite sixteen resonant partials.\n// ph0..ph15 set smoothed per-partial timing/phase.\n// s0..s15 set lifetime: fast lanes flash, slow lanes ring.\n// h0..h15 are partial ratios. Defaults are harmonic 1..16, but these can\n// later be replaced by Hamiltonian energy-gap ratios.\n\nParam m0(0);\nParam m1(0);\nParam m2(0);\nParam m3(0);\nParam m4(0);\nParam m5(0);\nParam m6(0);\nParam m7(0);\nParam m8(0);\nParam m9(0);\nParam m10(0);\nParam m11(0);\nParam m12(0);\nParam m13(0);\nParam m14(0);\nParam m15(0);\n\nParam ph0(0);\nParam ph1(0);\nParam ph2(0);\nParam ph3(0);\nParam ph4(0);\nParam ph5(0);\nParam ph6(0);\nParam ph7(0);\nParam ph8(0);\nParam ph9(0);\nParam ph10(0);\nParam ph11(0);\nParam ph12(0);\nParam ph13(0);\nParam ph14(0);\nParam ph15(0);\n\nParam s0(0);\nParam s1(0);\nParam s2(0);\nParam s3(0);\nParam s4(0);\nParam s5(0);\nParam s6(0);\nParam s7(0);\nParam s8(0);\nParam s9(0);\nParam s10(0);\nParam s11(0);\nParam s12(0);\nParam s13(0);\nParam s14(0);\nParam s15(0);\n\nParam h0(1);\nParam h1(2);\nParam h2(3);\nParam h3(4);\nParam h4(5);\nParam h5(6);\nParam h6(7);\nParam h7(8);\nParam h8(9);\nParam h9(10);\nParam h10(11);\nParam h11(12);\nParam h12(13);\nParam h13(14);\nParam h14(15);\nParam h15(16);\n\nParam purity(1);\nParam entropy(0);\nParam coherence(0);\nParam amp(0.2);\nParam default_freq(55);\nParam attack_ms(12);\nParam slow_decay_ms(900);\nParam fast_decay_ms(70);\nParam phase_smooth_ms(100);\nParam magnitude_smooth_ms(100);\nParam brightness(0.65);\nParam mix_voices(4);\nParam output_ceiling(0.85);\n\nHistory p0(0);\nHistory p1(0);\nHistory p2(0);\nHistory p3(0);\nHistory p4(0);\nHistory p5(0);\nHistory p6(0);\nHistory p7(0);\nHistory p8(0);\nHistory p9(0);\nHistory p10(0);\nHistory p11(0);\nHistory p12(0);\nHistory p13(0);\nHistory p14(0);\nHistory p15(0);\n\nHistory e0(0);\nHistory e1(0);\nHistory e2(0);\nHistory e3(0);\nHistory e4(0);\nHistory e5(0);\nHistory e6(0);\nHistory e7(0);\nHistory e8(0);\nHistory e9(0);\nHistory e10(0);\nHistory e11(0);\nHistory e12(0);\nHistory e13(0);\nHistory e14(0);\nHistory e15(0);\n\nHistory sm0(0);\nHistory sm1(0);\nHistory sm2(0);\nHistory sm3(0);\nHistory sm4(0);\nHistory sm5(0);\nHistory sm6(0);\nHistory sm7(0);\nHistory sm8(0);\nHistory sm9(0);\nHistory sm10(0);\nHistory sm11(0);\nHistory sm12(0);\nHistory sm13(0);\nHistory sm14(0);\nHistory sm15(0);\n\nHistory sph0(0);\nHistory sph1(0);\nHistory sph2(0);\nHistory sph3(0);\nHistory sph4(0);\nHistory sph5(0);\nHistory sph6(0);\nHistory sph7(0);\nHistory sph8(0);\nHistory sph9(0);\nHistory sph10(0);\nHistory sph11(0);\nHistory sph12(0);\nHistory sph13(0);\nHistory sph14(0);\nHistory sph15(0);\n\nfreq = (in1 > 0) * in1 + (in1 <= 0) * default_freq;\npur = clamp(purity, 0, 1);\nent = clamp(entropy, 0, 1);\ncoh = clamp(coherence, 0, 1);\n\nmag_ms = max(magnitude_smooth_ms, 0.1);\nmag_coeff = exp(-1 / (mag_ms * 0.001 * samplerate));\n\ntm0 = clamp(m0, 0, 1);\ntm1 = clamp(m1, 0, 1);\ntm2 = clamp(m2, 0, 1);\ntm3 = clamp(m3, 0, 1);\ntm4 = clamp(m4, 0, 1);\ntm5 = clamp(m5, 0, 1);\ntm6 = clamp(m6, 0, 1);\ntm7 = clamp(m7, 0, 1);\ntm8 = clamp(m8, 0, 1);\ntm9 = clamp(m9, 0, 1);\ntm10 = clamp(m10, 0, 1);\ntm11 = clamp(m11, 0, 1);\ntm12 = clamp(m12, 0, 1);\ntm13 = clamp(m13, 0, 1);\ntm14 = clamp(m14, 0, 1);\ntm15 = clamp(m15, 0, 1);\n\nsm0 = tm0 + mag_coeff * (sm0 - tm0);\nsm1 = tm1 + mag_coeff * (sm1 - tm1);\nsm2 = tm2 + mag_coeff * (sm2 - tm2);\nsm3 = tm3 + mag_coeff * (sm3 - tm3);\nsm4 = tm4 + mag_coeff * (sm4 - tm4);\nsm5 = tm5 + mag_coeff * (sm5 - tm5);\nsm6 = tm6 + mag_coeff * (sm6 - tm6);\nsm7 = tm7 + mag_coeff * (sm7 - tm7);\nsm8 = tm8 + mag_coeff * (sm8 - tm8);\nsm9 = tm9 + mag_coeff * (sm9 - tm9);\nsm10 = tm10 + mag_coeff * (sm10 - tm10);\nsm11 = tm11 + mag_coeff * (sm11 - tm11);\nsm12 = tm12 + mag_coeff * (sm12 - tm12);\nsm13 = tm13 + mag_coeff * (sm13 - tm13);\nsm14 = tm14 + mag_coeff * (sm14 - tm14);\nsm15 = tm15 + mag_coeff * (sm15 - tm15);\n\nphase_ms = max(phase_smooth_ms, 0.1);\nphase_coeff = exp(-1 / (phase_ms * 0.001 * samplerate));\n\ndph0 = atan2(sin(ph0 - sph0), cos(ph0 - sph0));\ndph1 = atan2(sin(ph1 - sph1), cos(ph1 - sph1));\ndph2 = atan2(sin(ph2 - sph2), cos(ph2 - sph2));\ndph3 = atan2(sin(ph3 - sph3), cos(ph3 - sph3));\ndph4 = atan2(sin(ph4 - sph4), cos(ph4 - sph4));\ndph5 = atan2(sin(ph5 - sph5), cos(ph5 - sph5));\ndph6 = atan2(sin(ph6 - sph6), cos(ph6 - sph6));\ndph7 = atan2(sin(ph7 - sph7), cos(ph7 - sph7));\ndph8 = atan2(sin(ph8 - sph8), cos(ph8 - sph8));\ndph9 = atan2(sin(ph9 - sph9), cos(ph9 - sph9));\ndph10 = atan2(sin(ph10 - sph10), cos(ph10 - sph10));\ndph11 = atan2(sin(ph11 - sph11), cos(ph11 - sph11));\ndph12 = atan2(sin(ph12 - sph12), cos(ph12 - sph12));\ndph13 = atan2(sin(ph13 - sph13), cos(ph13 - sph13));\ndph14 = atan2(sin(ph14 - sph14), cos(ph14 - sph14));\ndph15 = atan2(sin(ph15 - sph15), cos(ph15 - sph15));\n\nsph0 = sph0 + (1 - phase_coeff) * dph0;\nsph1 = sph1 + (1 - phase_coeff) * dph1;\nsph2 = sph2 + (1 - phase_coeff) * dph2;\nsph3 = sph3 + (1 - phase_coeff) * dph3;\nsph4 = sph4 + (1 - phase_coeff) * dph4;\nsph5 = sph5 + (1 - phase_coeff) * dph5;\nsph6 = sph6 + (1 - phase_coeff) * dph6;\nsph7 = sph7 + (1 - phase_coeff) * dph7;\nsph8 = sph8 + (1 - phase_coeff) * dph8;\nsph9 = sph9 + (1 - phase_coeff) * dph9;\nsph10 = sph10 + (1 - phase_coeff) * dph10;\nsph11 = sph11 + (1 - phase_coeff) * dph11;\nsph12 = sph12 + (1 - phase_coeff) * dph12;\nsph13 = sph13 + (1 - phase_coeff) * dph13;\nsph14 = sph14 + (1 - phase_coeff) * dph14;\nsph15 = sph15 + (1 - phase_coeff) * dph15;\n\natk_ms = max(attack_ms * mix(1.35, 0.65, coh), 0.1);\natk_coeff = exp(-1 / (atk_ms * 0.001 * samplerate));\n\nspd0 = clamp(abs(s0), 0, 1);\nspd1 = clamp(abs(s1), 0, 1);\nspd2 = clamp(abs(s2), 0, 1);\nspd3 = clamp(abs(s3), 0, 1);\nspd4 = clamp(abs(s4), 0, 1);\nspd5 = clamp(abs(s5), 0, 1);\nspd6 = clamp(abs(s6), 0, 1);\nspd7 = clamp(abs(s7), 0, 1);\nspd8 = clamp(abs(s8), 0, 1);\nspd9 = clamp(abs(s9), 0, 1);\nspd10 = clamp(abs(s10), 0, 1);\nspd11 = clamp(abs(s11), 0, 1);\nspd12 = clamp(abs(s12), 0, 1);\nspd13 = clamp(abs(s13), 0, 1);\nspd14 = clamp(abs(s14), 0, 1);\nspd15 = clamp(abs(s15), 0, 1);\n\ndec0 = mix(slow_decay_ms, fast_decay_ms, spd0);\ndec1 = mix(slow_decay_ms, fast_decay_ms, spd1);\ndec2 = mix(slow_decay_ms, fast_decay_ms, spd2);\ndec3 = mix(slow_decay_ms, fast_decay_ms, spd3);\ndec4 = mix(slow_decay_ms, fast_decay_ms, spd4);\ndec5 = mix(slow_decay_ms, fast_decay_ms, spd5);\ndec6 = mix(slow_decay_ms, fast_decay_ms, spd6);\ndec7 = mix(slow_decay_ms, fast_decay_ms, spd7);\ndec8 = mix(slow_decay_ms, fast_decay_ms, spd8);\ndec9 = mix(slow_decay_ms, fast_decay_ms, spd9);\ndec10 = mix(slow_decay_ms, fast_decay_ms, spd10);\ndec11 = mix(slow_decay_ms, fast_decay_ms, spd11);\ndec12 = mix(slow_decay_ms, fast_decay_ms, spd12);\ndec13 = mix(slow_decay_ms, fast_decay_ms, spd13);\ndec14 = mix(slow_decay_ms, fast_decay_ms, spd14);\ndec15 = mix(slow_decay_ms, fast_decay_ms, spd15);\n\ndc0 = exp(-1 / (max(dec0, 0.1) * 0.001 * samplerate));\ndc1 = exp(-1 / (max(dec1, 0.1) * 0.001 * samplerate));\ndc2 = exp(-1 / (max(dec2, 0.1) * 0.001 * samplerate));\ndc3 = exp(-1 / (max(dec3, 0.1) * 0.001 * samplerate));\ndc4 = exp(-1 / (max(dec4, 0.1) * 0.001 * samplerate));\ndc5 = exp(-1 / (max(dec5, 0.1) * 0.001 * samplerate));\ndc6 = exp(-1 / (max(dec6, 0.1) * 0.001 * samplerate));\ndc7 = exp(-1 / (max(dec7, 0.1) * 0.001 * samplerate));\ndc8 = exp(-1 / (max(dec8, 0.1) * 0.001 * samplerate));\ndc9 = exp(-1 / (max(dec9, 0.1) * 0.001 * samplerate));\ndc10 = exp(-1 / (max(dec10, 0.1) * 0.001 * samplerate));\ndc11 = exp(-1 / (max(dec11, 0.1) * 0.001 * samplerate));\ndc12 = exp(-1 / (max(dec12, 0.1) * 0.001 * samplerate));\ndc13 = exp(-1 / (max(dec13, 0.1) * 0.001 * samplerate));\ndc14 = exp(-1 / (max(dec14, 0.1) * 0.001 * samplerate));\ndc15 = exp(-1 / (max(dec15, 0.1) * 0.001 * samplerate));\n\n// Higher entropy lifts weaker modes. Higher purity makes excitation more selective.\nexc_shape = mix(0.55, 1.6, pur);\nt0 = pow(sm0 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt1 = pow(sm1 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt2 = pow(sm2 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt3 = pow(sm3 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt4 = pow(sm4 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt5 = pow(sm5 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt6 = pow(sm6 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt7 = pow(sm7 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt8 = pow(sm8 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt9 = pow(sm9 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt10 = pow(sm10 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt11 = pow(sm11 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt12 = pow(sm12 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt13 = pow(sm13 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt14 = pow(sm14 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt15 = pow(sm15 + 0.00001, exc_shape) * mix(0.35, 1, ent);\n\ne0 = (t0 > e0) * (t0 + atk_coeff * (e0 - t0)) + (t0 <= e0) * (t0 + dc0 * (e0 - t0));\ne1 = (t1 > e1) * (t1 + atk_coeff * (e1 - t1)) + (t1 <= e1) * (t1 + dc1 * (e1 - t1));\ne2 = (t2 > e2) * (t2 + atk_coeff * (e2 - t2)) + (t2 <= e2) * (t2 + dc2 * (e2 - t2));\ne3 = (t3 > e3) * (t3 + atk_coeff * (e3 - t3)) + (t3 <= e3) * (t3 + dc3 * (e3 - t3));\ne4 = (t4 > e4) * (t4 + atk_coeff * (e4 - t4)) + (t4 <= e4) * (t4 + dc4 * (e4 - t4));\ne5 = (t5 > e5) * (t5 + atk_coeff * (e5 - t5)) + (t5 <= e5) * (t5 + dc5 * (e5 - t5));\ne6 = (t6 > e6) * (t6 + atk_coeff * (e6 - t6)) + (t6 <= e6) * (t6 + dc6 * (e6 - t6));\ne7 = (t7 > e7) * (t7 + atk_coeff * (e7 - t7)) + (t7 <= e7) * (t7 + dc7 * (e7 - t7));\ne8 = (t8 > e8) * (t8 + atk_coeff * (e8 - t8)) + (t8 <= e8) * (t8 + dc8 * (e8 - t8));\ne9 = (t9 > e9) * (t9 + atk_coeff * (e9 - t9)) + (t9 <= e9) * (t9 + dc9 * (e9 - t9));\ne10 = (t10 > e10) * (t10 + atk_coeff * (e10 - t10)) + (t10 <= e10) * (t10 + dc10 * (e10 - t10));\ne11 = (t11 > e11) * (t11 + atk_coeff * (e11 - t11)) + (t11 <= e11) * (t11 + dc11 * (e11 - t11));\ne12 = (t12 > e12) * (t12 + atk_coeff * (e12 - t12)) + (t12 <= e12) * (t12 + dc12 * (e12 - t12));\ne13 = (t13 > e13) * (t13 + atk_coeff * (e13 - t13)) + (t13 <= e13) * (t13 + dc13 * (e13 - t13));\ne14 = (t14 > e14) * (t14 + atk_coeff * (e14 - t14)) + (t14 <= e14) * (t14 + dc14 * (e14 - t14));\ne15 = (t15 > e15) * (t15 + atk_coeff * (e15 - t15)) + (t15 <= e15) * (t15 + dc15 * (e15 - t15));\n\nbright = clamp(brightness + ent * 0.25, 0, 1);\n\np0 = fract(p0 + freq * max(h0, 0.01) / samplerate);\np1 = fract(p1 + freq * max(h1, 0.01) / samplerate);\np2 = fract(p2 + freq * max(h2, 0.01) / samplerate);\np3 = fract(p3 + freq * max(h3, 0.01) / samplerate);\np4 = fract(p4 + freq * max(h4, 0.01) / samplerate);\np5 = fract(p5 + freq * max(h5, 0.01) / samplerate);\np6 = fract(p6 + freq * max(h6, 0.01) / samplerate);\np7 = fract(p7 + freq * max(h7, 0.01) / samplerate);\np8 = fract(p8 + freq * max(h8, 0.01) / samplerate);\np9 = fract(p9 + freq * max(h9, 0.01) / samplerate);\np10 = fract(p10 + freq * max(h10, 0.01) / samplerate);\np11 = fract(p11 + freq * max(h11, 0.01) / samplerate);\np12 = fract(p12 + freq * max(h12, 0.01) / samplerate);\np13 = fract(p13 + freq * max(h13, 0.01) / samplerate);\np14 = fract(p14 + freq * max(h14, 0.01) / samplerate);\np15 = fract(p15 + freq * max(h15, 0.01) / samplerate);\n\ntwopi = 6.283185307179586;\npartials =\n    e0 * sin(twopi * p0 + sph0) / pow(max(h0, 1), bright) +\n    e1 * sin(twopi * p1 + sph1) / pow(max(h1, 1), bright) +\n    e2 * sin(twopi * p2 + sph2) / pow(max(h2, 1), bright) +\n    e3 * sin(twopi * p3 + sph3) / pow(max(h3, 1), bright) +\n    e4 * sin(twopi * p4 + sph4) / pow(max(h4, 1), bright) +\n    e5 * sin(twopi * p5 + sph5) / pow(max(h5, 1), bright) +\n    e6 * sin(twopi * p6 + sph6) / pow(max(h6, 1), bright) +\n    e7 * sin(twopi * p7 + sph7) / pow(max(h7, 1), bright) +\n    e8 * sin(twopi * p8 + sph8) / pow(max(h8, 1), bright) +\n    e9 * sin(twopi * p9 + sph9) / pow(max(h9, 1), bright) +\n    e10 * sin(twopi * p10 + sph10) / pow(max(h10, 1), bright) +\n    e11 * sin(twopi * p11 + sph11) / pow(max(h11, 1), bright) +\n    e12 * sin(twopi * p12 + sph12) / pow(max(h12, 1), bright) +\n    e13 * sin(twopi * p13 + sph13) / pow(max(h13, 1), bright) +\n    e14 * sin(twopi * p14 + sph14) / pow(max(h14, 1), bright) +\n    e15 * sin(twopi * p15 + sph15) / pow(max(h15, 1), bright);\n\nvoice_scale = 1 / sqrt(max(mix_voices, 1));\nsig = tanh(partials * 0.5);\n\nout1 = sig * amp * output_ceiling * voice_scale;\nout2 = e0 + e1 + e2 + e3 + e4 + e5 + e6 + e7 + e8 + e9 + e10 + e11 + e12 + e13 + e14 + e15;\nout3 = freq;\n",
					"fontface" : 0,
					"fontname" : "<Monospaced>",
					"fontsize" : 12.0,
					"id" : "obj-42",
					"maxclass" : "gen.codebox~",
					"numinlets" : 1,
					"numoutlets" : 3,
					"outlettype" : [ "signal", "signal", "signal" ],
					"patching_rect" : [ 713.333354592323303, 490.666681289672852, 88.00000262260437, 42.666667938232422 ]
				}

			}
, 			{
				"box" : 				{
					"automatic" : 1,
					"id" : "obj-38",
					"maxclass" : "scope~",
					"numinlets" : 2,
					"numoutlets" : 0,
					"patching_rect" : [ 698.666687488555908, 729.333355069160461, 130.0, 130.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-36",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1158.000003814697266, 354.666677236557007, 79.0, 22.0 ],
					"text" : "prepend amp"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "obj-37",
					"maxclass" : "flonum",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 1151.33333694934845, 294.666675448417664, 50.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-34",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 961.0, 413.0, 31.0, 22.0 ],
					"text" : "sig~"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "obj-35",
					"maxclass" : "flonum",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 959.0, 370.0, 50.0, 22.0 ]
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
					"patching_rect" : [ 688.000020503997803, 621.333351850509644, 50.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-32",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 581.333350658416748, 648.000019311904907, 34.0, 22.0 ],
					"text" : "*~ 1."
				}

			}
, 			{
				"box" : 				{
					"code" : "// QMW Density Field Quantum Resonator 16\n//\n// Gen~ codebox.\n// in1 is the carrier frequency in Hz.\n// m0..m15 excite sixteen resonant partials.\n// ph0..ph15 set smoothed per-partial timing/phase.\n// s0..s15 set lifetime: fast lanes flash, slow lanes ring.\n// h0..h15 are partial ratios. Defaults are harmonic 1..16, but these can\n// later be replaced by Hamiltonian energy-gap ratios.\n\nParam m0(0);\nParam m1(0);\nParam m2(0);\nParam m3(0);\nParam m4(0);\nParam m5(0);\nParam m6(0);\nParam m7(0);\nParam m8(0);\nParam m9(0);\nParam m10(0);\nParam m11(0);\nParam m12(0);\nParam m13(0);\nParam m14(0);\nParam m15(0);\n\nParam ph0(0);\nParam ph1(0);\nParam ph2(0);\nParam ph3(0);\nParam ph4(0);\nParam ph5(0);\nParam ph6(0);\nParam ph7(0);\nParam ph8(0);\nParam ph9(0);\nParam ph10(0);\nParam ph11(0);\nParam ph12(0);\nParam ph13(0);\nParam ph14(0);\nParam ph15(0);\n\nParam s0(0);\nParam s1(0);\nParam s2(0);\nParam s3(0);\nParam s4(0);\nParam s5(0);\nParam s6(0);\nParam s7(0);\nParam s8(0);\nParam s9(0);\nParam s10(0);\nParam s11(0);\nParam s12(0);\nParam s13(0);\nParam s14(0);\nParam s15(0);\n\nParam h0(1);\nParam h1(2);\nParam h2(3);\nParam h3(4);\nParam h4(5);\nParam h5(6);\nParam h6(7);\nParam h7(8);\nParam h8(9);\nParam h9(10);\nParam h10(11);\nParam h11(12);\nParam h12(13);\nParam h13(14);\nParam h14(15);\nParam h15(16);\n\nParam purity(1);\nParam entropy(0);\nParam coherence(0);\nParam amp(0.2);\nParam default_freq(55);\nParam attack_ms(12);\nParam slow_decay_ms(900);\nParam fast_decay_ms(70);\nParam phase_smooth_ms(100);\nParam magnitude_smooth_ms(100);\nParam brightness(0.65);\nParam mix_voices(4);\nParam output_ceiling(0.85);\n\nHistory p0(0);\nHistory p1(0);\nHistory p2(0);\nHistory p3(0);\nHistory p4(0);\nHistory p5(0);\nHistory p6(0);\nHistory p7(0);\nHistory p8(0);\nHistory p9(0);\nHistory p10(0);\nHistory p11(0);\nHistory p12(0);\nHistory p13(0);\nHistory p14(0);\nHistory p15(0);\n\nHistory e0(0);\nHistory e1(0);\nHistory e2(0);\nHistory e3(0);\nHistory e4(0);\nHistory e5(0);\nHistory e6(0);\nHistory e7(0);\nHistory e8(0);\nHistory e9(0);\nHistory e10(0);\nHistory e11(0);\nHistory e12(0);\nHistory e13(0);\nHistory e14(0);\nHistory e15(0);\n\nHistory sm0(0);\nHistory sm1(0);\nHistory sm2(0);\nHistory sm3(0);\nHistory sm4(0);\nHistory sm5(0);\nHistory sm6(0);\nHistory sm7(0);\nHistory sm8(0);\nHistory sm9(0);\nHistory sm10(0);\nHistory sm11(0);\nHistory sm12(0);\nHistory sm13(0);\nHistory sm14(0);\nHistory sm15(0);\n\nHistory sph0(0);\nHistory sph1(0);\nHistory sph2(0);\nHistory sph3(0);\nHistory sph4(0);\nHistory sph5(0);\nHistory sph6(0);\nHistory sph7(0);\nHistory sph8(0);\nHistory sph9(0);\nHistory sph10(0);\nHistory sph11(0);\nHistory sph12(0);\nHistory sph13(0);\nHistory sph14(0);\nHistory sph15(0);\n\nfreq = (in1 > 0) * in1 + (in1 <= 0) * default_freq;\npur = clamp(purity, 0, 1);\nent = clamp(entropy, 0, 1);\ncoh = clamp(coherence, 0, 1);\n\nmag_ms = max(magnitude_smooth_ms, 0.1);\nmag_coeff = exp(-1 / (mag_ms * 0.001 * samplerate));\n\ntm0 = clamp(m0, 0, 1);\ntm1 = clamp(m1, 0, 1);\ntm2 = clamp(m2, 0, 1);\ntm3 = clamp(m3, 0, 1);\ntm4 = clamp(m4, 0, 1);\ntm5 = clamp(m5, 0, 1);\ntm6 = clamp(m6, 0, 1);\ntm7 = clamp(m7, 0, 1);\ntm8 = clamp(m8, 0, 1);\ntm9 = clamp(m9, 0, 1);\ntm10 = clamp(m10, 0, 1);\ntm11 = clamp(m11, 0, 1);\ntm12 = clamp(m12, 0, 1);\ntm13 = clamp(m13, 0, 1);\ntm14 = clamp(m14, 0, 1);\ntm15 = clamp(m15, 0, 1);\n\nsm0 = tm0 + mag_coeff * (sm0 - tm0);\nsm1 = tm1 + mag_coeff * (sm1 - tm1);\nsm2 = tm2 + mag_coeff * (sm2 - tm2);\nsm3 = tm3 + mag_coeff * (sm3 - tm3);\nsm4 = tm4 + mag_coeff * (sm4 - tm4);\nsm5 = tm5 + mag_coeff * (sm5 - tm5);\nsm6 = tm6 + mag_coeff * (sm6 - tm6);\nsm7 = tm7 + mag_coeff * (sm7 - tm7);\nsm8 = tm8 + mag_coeff * (sm8 - tm8);\nsm9 = tm9 + mag_coeff * (sm9 - tm9);\nsm10 = tm10 + mag_coeff * (sm10 - tm10);\nsm11 = tm11 + mag_coeff * (sm11 - tm11);\nsm12 = tm12 + mag_coeff * (sm12 - tm12);\nsm13 = tm13 + mag_coeff * (sm13 - tm13);\nsm14 = tm14 + mag_coeff * (sm14 - tm14);\nsm15 = tm15 + mag_coeff * (sm15 - tm15);\n\nphase_ms = max(phase_smooth_ms, 0.1);\nphase_coeff = exp(-1 / (phase_ms * 0.001 * samplerate));\n\ndph0 = atan2(sin(ph0 - sph0), cos(ph0 - sph0));\ndph1 = atan2(sin(ph1 - sph1), cos(ph1 - sph1));\ndph2 = atan2(sin(ph2 - sph2), cos(ph2 - sph2));\ndph3 = atan2(sin(ph3 - sph3), cos(ph3 - sph3));\ndph4 = atan2(sin(ph4 - sph4), cos(ph4 - sph4));\ndph5 = atan2(sin(ph5 - sph5), cos(ph5 - sph5));\ndph6 = atan2(sin(ph6 - sph6), cos(ph6 - sph6));\ndph7 = atan2(sin(ph7 - sph7), cos(ph7 - sph7));\ndph8 = atan2(sin(ph8 - sph8), cos(ph8 - sph8));\ndph9 = atan2(sin(ph9 - sph9), cos(ph9 - sph9));\ndph10 = atan2(sin(ph10 - sph10), cos(ph10 - sph10));\ndph11 = atan2(sin(ph11 - sph11), cos(ph11 - sph11));\ndph12 = atan2(sin(ph12 - sph12), cos(ph12 - sph12));\ndph13 = atan2(sin(ph13 - sph13), cos(ph13 - sph13));\ndph14 = atan2(sin(ph14 - sph14), cos(ph14 - sph14));\ndph15 = atan2(sin(ph15 - sph15), cos(ph15 - sph15));\n\nsph0 = sph0 + (1 - phase_coeff) * dph0;\nsph1 = sph1 + (1 - phase_coeff) * dph1;\nsph2 = sph2 + (1 - phase_coeff) * dph2;\nsph3 = sph3 + (1 - phase_coeff) * dph3;\nsph4 = sph4 + (1 - phase_coeff) * dph4;\nsph5 = sph5 + (1 - phase_coeff) * dph5;\nsph6 = sph6 + (1 - phase_coeff) * dph6;\nsph7 = sph7 + (1 - phase_coeff) * dph7;\nsph8 = sph8 + (1 - phase_coeff) * dph8;\nsph9 = sph9 + (1 - phase_coeff) * dph9;\nsph10 = sph10 + (1 - phase_coeff) * dph10;\nsph11 = sph11 + (1 - phase_coeff) * dph11;\nsph12 = sph12 + (1 - phase_coeff) * dph12;\nsph13 = sph13 + (1 - phase_coeff) * dph13;\nsph14 = sph14 + (1 - phase_coeff) * dph14;\nsph15 = sph15 + (1 - phase_coeff) * dph15;\n\natk_ms = max(attack_ms * mix(1.35, 0.65, coh), 0.1);\natk_coeff = exp(-1 / (atk_ms * 0.001 * samplerate));\n\nspd0 = clamp(abs(s0), 0, 1);\nspd1 = clamp(abs(s1), 0, 1);\nspd2 = clamp(abs(s2), 0, 1);\nspd3 = clamp(abs(s3), 0, 1);\nspd4 = clamp(abs(s4), 0, 1);\nspd5 = clamp(abs(s5), 0, 1);\nspd6 = clamp(abs(s6), 0, 1);\nspd7 = clamp(abs(s7), 0, 1);\nspd8 = clamp(abs(s8), 0, 1);\nspd9 = clamp(abs(s9), 0, 1);\nspd10 = clamp(abs(s10), 0, 1);\nspd11 = clamp(abs(s11), 0, 1);\nspd12 = clamp(abs(s12), 0, 1);\nspd13 = clamp(abs(s13), 0, 1);\nspd14 = clamp(abs(s14), 0, 1);\nspd15 = clamp(abs(s15), 0, 1);\n\ndec0 = mix(slow_decay_ms, fast_decay_ms, spd0);\ndec1 = mix(slow_decay_ms, fast_decay_ms, spd1);\ndec2 = mix(slow_decay_ms, fast_decay_ms, spd2);\ndec3 = mix(slow_decay_ms, fast_decay_ms, spd3);\ndec4 = mix(slow_decay_ms, fast_decay_ms, spd4);\ndec5 = mix(slow_decay_ms, fast_decay_ms, spd5);\ndec6 = mix(slow_decay_ms, fast_decay_ms, spd6);\ndec7 = mix(slow_decay_ms, fast_decay_ms, spd7);\ndec8 = mix(slow_decay_ms, fast_decay_ms, spd8);\ndec9 = mix(slow_decay_ms, fast_decay_ms, spd9);\ndec10 = mix(slow_decay_ms, fast_decay_ms, spd10);\ndec11 = mix(slow_decay_ms, fast_decay_ms, spd11);\ndec12 = mix(slow_decay_ms, fast_decay_ms, spd12);\ndec13 = mix(slow_decay_ms, fast_decay_ms, spd13);\ndec14 = mix(slow_decay_ms, fast_decay_ms, spd14);\ndec15 = mix(slow_decay_ms, fast_decay_ms, spd15);\n\ndc0 = exp(-1 / (max(dec0, 0.1) * 0.001 * samplerate));\ndc1 = exp(-1 / (max(dec1, 0.1) * 0.001 * samplerate));\ndc2 = exp(-1 / (max(dec2, 0.1) * 0.001 * samplerate));\ndc3 = exp(-1 / (max(dec3, 0.1) * 0.001 * samplerate));\ndc4 = exp(-1 / (max(dec4, 0.1) * 0.001 * samplerate));\ndc5 = exp(-1 / (max(dec5, 0.1) * 0.001 * samplerate));\ndc6 = exp(-1 / (max(dec6, 0.1) * 0.001 * samplerate));\ndc7 = exp(-1 / (max(dec7, 0.1) * 0.001 * samplerate));\ndc8 = exp(-1 / (max(dec8, 0.1) * 0.001 * samplerate));\ndc9 = exp(-1 / (max(dec9, 0.1) * 0.001 * samplerate));\ndc10 = exp(-1 / (max(dec10, 0.1) * 0.001 * samplerate));\ndc11 = exp(-1 / (max(dec11, 0.1) * 0.001 * samplerate));\ndc12 = exp(-1 / (max(dec12, 0.1) * 0.001 * samplerate));\ndc13 = exp(-1 / (max(dec13, 0.1) * 0.001 * samplerate));\ndc14 = exp(-1 / (max(dec14, 0.1) * 0.001 * samplerate));\ndc15 = exp(-1 / (max(dec15, 0.1) * 0.001 * samplerate));\n\n// Higher entropy lifts weaker modes. Higher purity makes excitation more selective.\nexc_shape = mix(0.55, 1.6, pur);\nt0 = pow(sm0 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt1 = pow(sm1 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt2 = pow(sm2 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt3 = pow(sm3 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt4 = pow(sm4 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt5 = pow(sm5 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt6 = pow(sm6 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt7 = pow(sm7 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt8 = pow(sm8 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt9 = pow(sm9 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt10 = pow(sm10 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt11 = pow(sm11 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt12 = pow(sm12 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt13 = pow(sm13 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt14 = pow(sm14 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt15 = pow(sm15 + 0.00001, exc_shape) * mix(0.35, 1, ent);\n\ne0 = (t0 > e0) * (t0 + atk_coeff * (e0 - t0)) + (t0 <= e0) * (t0 + dc0 * (e0 - t0));\ne1 = (t1 > e1) * (t1 + atk_coeff * (e1 - t1)) + (t1 <= e1) * (t1 + dc1 * (e1 - t1));\ne2 = (t2 > e2) * (t2 + atk_coeff * (e2 - t2)) + (t2 <= e2) * (t2 + dc2 * (e2 - t2));\ne3 = (t3 > e3) * (t3 + atk_coeff * (e3 - t3)) + (t3 <= e3) * (t3 + dc3 * (e3 - t3));\ne4 = (t4 > e4) * (t4 + atk_coeff * (e4 - t4)) + (t4 <= e4) * (t4 + dc4 * (e4 - t4));\ne5 = (t5 > e5) * (t5 + atk_coeff * (e5 - t5)) + (t5 <= e5) * (t5 + dc5 * (e5 - t5));\ne6 = (t6 > e6) * (t6 + atk_coeff * (e6 - t6)) + (t6 <= e6) * (t6 + dc6 * (e6 - t6));\ne7 = (t7 > e7) * (t7 + atk_coeff * (e7 - t7)) + (t7 <= e7) * (t7 + dc7 * (e7 - t7));\ne8 = (t8 > e8) * (t8 + atk_coeff * (e8 - t8)) + (t8 <= e8) * (t8 + dc8 * (e8 - t8));\ne9 = (t9 > e9) * (t9 + atk_coeff * (e9 - t9)) + (t9 <= e9) * (t9 + dc9 * (e9 - t9));\ne10 = (t10 > e10) * (t10 + atk_coeff * (e10 - t10)) + (t10 <= e10) * (t10 + dc10 * (e10 - t10));\ne11 = (t11 > e11) * (t11 + atk_coeff * (e11 - t11)) + (t11 <= e11) * (t11 + dc11 * (e11 - t11));\ne12 = (t12 > e12) * (t12 + atk_coeff * (e12 - t12)) + (t12 <= e12) * (t12 + dc12 * (e12 - t12));\ne13 = (t13 > e13) * (t13 + atk_coeff * (e13 - t13)) + (t13 <= e13) * (t13 + dc13 * (e13 - t13));\ne14 = (t14 > e14) * (t14 + atk_coeff * (e14 - t14)) + (t14 <= e14) * (t14 + dc14 * (e14 - t14));\ne15 = (t15 > e15) * (t15 + atk_coeff * (e15 - t15)) + (t15 <= e15) * (t15 + dc15 * (e15 - t15));\n\nbright = clamp(brightness + ent * 0.25, 0, 1);\n\np0 = fract(p0 + freq * max(h0, 0.01) / samplerate);\np1 = fract(p1 + freq * max(h1, 0.01) / samplerate);\np2 = fract(p2 + freq * max(h2, 0.01) / samplerate);\np3 = fract(p3 + freq * max(h3, 0.01) / samplerate);\np4 = fract(p4 + freq * max(h4, 0.01) / samplerate);\np5 = fract(p5 + freq * max(h5, 0.01) / samplerate);\np6 = fract(p6 + freq * max(h6, 0.01) / samplerate);\np7 = fract(p7 + freq * max(h7, 0.01) / samplerate);\np8 = fract(p8 + freq * max(h8, 0.01) / samplerate);\np9 = fract(p9 + freq * max(h9, 0.01) / samplerate);\np10 = fract(p10 + freq * max(h10, 0.01) / samplerate);\np11 = fract(p11 + freq * max(h11, 0.01) / samplerate);\np12 = fract(p12 + freq * max(h12, 0.01) / samplerate);\np13 = fract(p13 + freq * max(h13, 0.01) / samplerate);\np14 = fract(p14 + freq * max(h14, 0.01) / samplerate);\np15 = fract(p15 + freq * max(h15, 0.01) / samplerate);\n\ntwopi = 6.283185307179586;\npartials =\n    e0 * sin(twopi * p0 + sph0) / pow(max(h0, 1), bright) +\n    e1 * sin(twopi * p1 + sph1) / pow(max(h1, 1), bright) +\n    e2 * sin(twopi * p2 + sph2) / pow(max(h2, 1), bright) +\n    e3 * sin(twopi * p3 + sph3) / pow(max(h3, 1), bright) +\n    e4 * sin(twopi * p4 + sph4) / pow(max(h4, 1), bright) +\n    e5 * sin(twopi * p5 + sph5) / pow(max(h5, 1), bright) +\n    e6 * sin(twopi * p6 + sph6) / pow(max(h6, 1), bright) +\n    e7 * sin(twopi * p7 + sph7) / pow(max(h7, 1), bright) +\n    e8 * sin(twopi * p8 + sph8) / pow(max(h8, 1), bright) +\n    e9 * sin(twopi * p9 + sph9) / pow(max(h9, 1), bright) +\n    e10 * sin(twopi * p10 + sph10) / pow(max(h10, 1), bright) +\n    e11 * sin(twopi * p11 + sph11) / pow(max(h11, 1), bright) +\n    e12 * sin(twopi * p12 + sph12) / pow(max(h12, 1), bright) +\n    e13 * sin(twopi * p13 + sph13) / pow(max(h13, 1), bright) +\n    e14 * sin(twopi * p14 + sph14) / pow(max(h14, 1), bright) +\n    e15 * sin(twopi * p15 + sph15) / pow(max(h15, 1), bright);\n\nvoice_scale = 1 / sqrt(max(mix_voices, 1));\nsig = tanh(partials * 0.5);\n\nout1 = sig * amp * output_ceiling * voice_scale;\nout2 = e0 + e1 + e2 + e3 + e4 + e5 + e6 + e7 + e8 + e9 + e10 + e11 + e12 + e13 + e14 + e15;\nout3 = freq;\n",
					"fontface" : 0,
					"fontname" : "<Monospaced>",
					"fontsize" : 12.0,
					"id" : "obj-22",
					"maxclass" : "gen.codebox~",
					"numinlets" : 1,
					"numoutlets" : 3,
					"outlettype" : [ "signal", "signal", "signal" ],
					"patching_rect" : [ 545.333349585533142, 495.333348095417023, 148.000004410743713, 41.333334565162659 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-19",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1019.0, 306.0, 111.0, 22.0 ],
					"text" : "prepend attack_ms"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "obj-20",
					"maxclass" : "flonum",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 1012.0, 246.0, 50.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-18",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 1012.0, 197.0, 79.0, 22.0 ],
					"text" : "prepend amp"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "obj-17",
					"maxclass" : "flonum",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 1005.0, 137.0, 50.0, 22.0 ]
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
					"patching_rect" : [ 525.333348989486694, 733.333355188369751, 130.0, 130.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-10",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 828.0, 424.0, 89.0, 22.0 ],
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
					"patching_rect" : [ 657.33335292339325, 342.333331227302551, 89.0, 22.0 ],
					"text" : "prepend speed"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-7",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 569.333350300788879, 342.333331227302551, 82.0, 22.0 ],
					"text" : "prepend imag"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-6",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 480.000014305114746, 342.333331227302551, 76.0, 22.0 ],
					"text" : "prepend real"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-5",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 353.333343863487244, 342.333331227302551, 112.0, 22.0 ],
					"text" : "prepend magnitude"
				}

			}
, 			{
				"box" : 				{
					"code" : "// QMW Density Field Quantum Resonator 16\n//\n// Gen~ codebox.\n// in1 is the carrier frequency in Hz.\n// m0..m15 excite sixteen resonant partials.\n// ph0..ph15 set smoothed per-partial timing/phase.\n// s0..s15 set lifetime: fast lanes flash, slow lanes ring.\n// h0..h15 are partial ratios. Defaults are harmonic 1..16, but these can\n// later be replaced by Hamiltonian energy-gap ratios.\n\nParam m0(0);\nParam m1(0);\nParam m2(0);\nParam m3(0);\nParam m4(0);\nParam m5(0);\nParam m6(0);\nParam m7(0);\nParam m8(0);\nParam m9(0);\nParam m10(0);\nParam m11(0);\nParam m12(0);\nParam m13(0);\nParam m14(0);\nParam m15(0);\n\nParam ph0(0);\nParam ph1(0);\nParam ph2(0);\nParam ph3(0);\nParam ph4(0);\nParam ph5(0);\nParam ph6(0);\nParam ph7(0);\nParam ph8(0);\nParam ph9(0);\nParam ph10(0);\nParam ph11(0);\nParam ph12(0);\nParam ph13(0);\nParam ph14(0);\nParam ph15(0);\n\nParam s0(0);\nParam s1(0);\nParam s2(0);\nParam s3(0);\nParam s4(0);\nParam s5(0);\nParam s6(0);\nParam s7(0);\nParam s8(0);\nParam s9(0);\nParam s10(0);\nParam s11(0);\nParam s12(0);\nParam s13(0);\nParam s14(0);\nParam s15(0);\n\nParam h0(1);\nParam h1(2);\nParam h2(3);\nParam h3(4);\nParam h4(5);\nParam h5(6);\nParam h6(7);\nParam h7(8);\nParam h8(9);\nParam h9(10);\nParam h10(11);\nParam h11(12);\nParam h12(13);\nParam h13(14);\nParam h14(15);\nParam h15(16);\n\nParam purity(1);\nParam entropy(0);\nParam coherence(0);\nParam amp(0.2);\nParam default_freq(55);\nParam attack_ms(12);\nParam slow_decay_ms(900);\nParam fast_decay_ms(70);\nParam phase_smooth_ms(100);\nParam magnitude_smooth_ms(100);\nParam brightness(0.65);\nParam mix_voices(4);\nParam output_ceiling(0.85);\n\nHistory p0(0);\nHistory p1(0);\nHistory p2(0);\nHistory p3(0);\nHistory p4(0);\nHistory p5(0);\nHistory p6(0);\nHistory p7(0);\nHistory p8(0);\nHistory p9(0);\nHistory p10(0);\nHistory p11(0);\nHistory p12(0);\nHistory p13(0);\nHistory p14(0);\nHistory p15(0);\n\nHistory e0(0);\nHistory e1(0);\nHistory e2(0);\nHistory e3(0);\nHistory e4(0);\nHistory e5(0);\nHistory e6(0);\nHistory e7(0);\nHistory e8(0);\nHistory e9(0);\nHistory e10(0);\nHistory e11(0);\nHistory e12(0);\nHistory e13(0);\nHistory e14(0);\nHistory e15(0);\n\nHistory sm0(0);\nHistory sm1(0);\nHistory sm2(0);\nHistory sm3(0);\nHistory sm4(0);\nHistory sm5(0);\nHistory sm6(0);\nHistory sm7(0);\nHistory sm8(0);\nHistory sm9(0);\nHistory sm10(0);\nHistory sm11(0);\nHistory sm12(0);\nHistory sm13(0);\nHistory sm14(0);\nHistory sm15(0);\n\nHistory sph0(0);\nHistory sph1(0);\nHistory sph2(0);\nHistory sph3(0);\nHistory sph4(0);\nHistory sph5(0);\nHistory sph6(0);\nHistory sph7(0);\nHistory sph8(0);\nHistory sph9(0);\nHistory sph10(0);\nHistory sph11(0);\nHistory sph12(0);\nHistory sph13(0);\nHistory sph14(0);\nHistory sph15(0);\n\nfreq = (in1 > 0) * in1 + (in1 <= 0) * default_freq;\npur = clamp(purity, 0, 1);\nent = clamp(entropy, 0, 1);\ncoh = clamp(coherence, 0, 1);\n\nmag_ms = max(magnitude_smooth_ms, 0.1);\nmag_coeff = exp(-1 / (mag_ms * 0.001 * samplerate));\n\ntm0 = clamp(m0, 0, 1);\ntm1 = clamp(m1, 0, 1);\ntm2 = clamp(m2, 0, 1);\ntm3 = clamp(m3, 0, 1);\ntm4 = clamp(m4, 0, 1);\ntm5 = clamp(m5, 0, 1);\ntm6 = clamp(m6, 0, 1);\ntm7 = clamp(m7, 0, 1);\ntm8 = clamp(m8, 0, 1);\ntm9 = clamp(m9, 0, 1);\ntm10 = clamp(m10, 0, 1);\ntm11 = clamp(m11, 0, 1);\ntm12 = clamp(m12, 0, 1);\ntm13 = clamp(m13, 0, 1);\ntm14 = clamp(m14, 0, 1);\ntm15 = clamp(m15, 0, 1);\n\nsm0 = tm0 + mag_coeff * (sm0 - tm0);\nsm1 = tm1 + mag_coeff * (sm1 - tm1);\nsm2 = tm2 + mag_coeff * (sm2 - tm2);\nsm3 = tm3 + mag_coeff * (sm3 - tm3);\nsm4 = tm4 + mag_coeff * (sm4 - tm4);\nsm5 = tm5 + mag_coeff * (sm5 - tm5);\nsm6 = tm6 + mag_coeff * (sm6 - tm6);\nsm7 = tm7 + mag_coeff * (sm7 - tm7);\nsm8 = tm8 + mag_coeff * (sm8 - tm8);\nsm9 = tm9 + mag_coeff * (sm9 - tm9);\nsm10 = tm10 + mag_coeff * (sm10 - tm10);\nsm11 = tm11 + mag_coeff * (sm11 - tm11);\nsm12 = tm12 + mag_coeff * (sm12 - tm12);\nsm13 = tm13 + mag_coeff * (sm13 - tm13);\nsm14 = tm14 + mag_coeff * (sm14 - tm14);\nsm15 = tm15 + mag_coeff * (sm15 - tm15);\n\nphase_ms = max(phase_smooth_ms, 0.1);\nphase_coeff = exp(-1 / (phase_ms * 0.001 * samplerate));\n\ndph0 = atan2(sin(ph0 - sph0), cos(ph0 - sph0));\ndph1 = atan2(sin(ph1 - sph1), cos(ph1 - sph1));\ndph2 = atan2(sin(ph2 - sph2), cos(ph2 - sph2));\ndph3 = atan2(sin(ph3 - sph3), cos(ph3 - sph3));\ndph4 = atan2(sin(ph4 - sph4), cos(ph4 - sph4));\ndph5 = atan2(sin(ph5 - sph5), cos(ph5 - sph5));\ndph6 = atan2(sin(ph6 - sph6), cos(ph6 - sph6));\ndph7 = atan2(sin(ph7 - sph7), cos(ph7 - sph7));\ndph8 = atan2(sin(ph8 - sph8), cos(ph8 - sph8));\ndph9 = atan2(sin(ph9 - sph9), cos(ph9 - sph9));\ndph10 = atan2(sin(ph10 - sph10), cos(ph10 - sph10));\ndph11 = atan2(sin(ph11 - sph11), cos(ph11 - sph11));\ndph12 = atan2(sin(ph12 - sph12), cos(ph12 - sph12));\ndph13 = atan2(sin(ph13 - sph13), cos(ph13 - sph13));\ndph14 = atan2(sin(ph14 - sph14), cos(ph14 - sph14));\ndph15 = atan2(sin(ph15 - sph15), cos(ph15 - sph15));\n\nsph0 = sph0 + (1 - phase_coeff) * dph0;\nsph1 = sph1 + (1 - phase_coeff) * dph1;\nsph2 = sph2 + (1 - phase_coeff) * dph2;\nsph3 = sph3 + (1 - phase_coeff) * dph3;\nsph4 = sph4 + (1 - phase_coeff) * dph4;\nsph5 = sph5 + (1 - phase_coeff) * dph5;\nsph6 = sph6 + (1 - phase_coeff) * dph6;\nsph7 = sph7 + (1 - phase_coeff) * dph7;\nsph8 = sph8 + (1 - phase_coeff) * dph8;\nsph9 = sph9 + (1 - phase_coeff) * dph9;\nsph10 = sph10 + (1 - phase_coeff) * dph10;\nsph11 = sph11 + (1 - phase_coeff) * dph11;\nsph12 = sph12 + (1 - phase_coeff) * dph12;\nsph13 = sph13 + (1 - phase_coeff) * dph13;\nsph14 = sph14 + (1 - phase_coeff) * dph14;\nsph15 = sph15 + (1 - phase_coeff) * dph15;\n\natk_ms = max(attack_ms * mix(1.35, 0.65, coh), 0.1);\natk_coeff = exp(-1 / (atk_ms * 0.001 * samplerate));\n\nspd0 = clamp(abs(s0), 0, 1);\nspd1 = clamp(abs(s1), 0, 1);\nspd2 = clamp(abs(s2), 0, 1);\nspd3 = clamp(abs(s3), 0, 1);\nspd4 = clamp(abs(s4), 0, 1);\nspd5 = clamp(abs(s5), 0, 1);\nspd6 = clamp(abs(s6), 0, 1);\nspd7 = clamp(abs(s7), 0, 1);\nspd8 = clamp(abs(s8), 0, 1);\nspd9 = clamp(abs(s9), 0, 1);\nspd10 = clamp(abs(s10), 0, 1);\nspd11 = clamp(abs(s11), 0, 1);\nspd12 = clamp(abs(s12), 0, 1);\nspd13 = clamp(abs(s13), 0, 1);\nspd14 = clamp(abs(s14), 0, 1);\nspd15 = clamp(abs(s15), 0, 1);\n\ndec0 = mix(slow_decay_ms, fast_decay_ms, spd0);\ndec1 = mix(slow_decay_ms, fast_decay_ms, spd1);\ndec2 = mix(slow_decay_ms, fast_decay_ms, spd2);\ndec3 = mix(slow_decay_ms, fast_decay_ms, spd3);\ndec4 = mix(slow_decay_ms, fast_decay_ms, spd4);\ndec5 = mix(slow_decay_ms, fast_decay_ms, spd5);\ndec6 = mix(slow_decay_ms, fast_decay_ms, spd6);\ndec7 = mix(slow_decay_ms, fast_decay_ms, spd7);\ndec8 = mix(slow_decay_ms, fast_decay_ms, spd8);\ndec9 = mix(slow_decay_ms, fast_decay_ms, spd9);\ndec10 = mix(slow_decay_ms, fast_decay_ms, spd10);\ndec11 = mix(slow_decay_ms, fast_decay_ms, spd11);\ndec12 = mix(slow_decay_ms, fast_decay_ms, spd12);\ndec13 = mix(slow_decay_ms, fast_decay_ms, spd13);\ndec14 = mix(slow_decay_ms, fast_decay_ms, spd14);\ndec15 = mix(slow_decay_ms, fast_decay_ms, spd15);\n\ndc0 = exp(-1 / (max(dec0, 0.1) * 0.001 * samplerate));\ndc1 = exp(-1 / (max(dec1, 0.1) * 0.001 * samplerate));\ndc2 = exp(-1 / (max(dec2, 0.1) * 0.001 * samplerate));\ndc3 = exp(-1 / (max(dec3, 0.1) * 0.001 * samplerate));\ndc4 = exp(-1 / (max(dec4, 0.1) * 0.001 * samplerate));\ndc5 = exp(-1 / (max(dec5, 0.1) * 0.001 * samplerate));\ndc6 = exp(-1 / (max(dec6, 0.1) * 0.001 * samplerate));\ndc7 = exp(-1 / (max(dec7, 0.1) * 0.001 * samplerate));\ndc8 = exp(-1 / (max(dec8, 0.1) * 0.001 * samplerate));\ndc9 = exp(-1 / (max(dec9, 0.1) * 0.001 * samplerate));\ndc10 = exp(-1 / (max(dec10, 0.1) * 0.001 * samplerate));\ndc11 = exp(-1 / (max(dec11, 0.1) * 0.001 * samplerate));\ndc12 = exp(-1 / (max(dec12, 0.1) * 0.001 * samplerate));\ndc13 = exp(-1 / (max(dec13, 0.1) * 0.001 * samplerate));\ndc14 = exp(-1 / (max(dec14, 0.1) * 0.001 * samplerate));\ndc15 = exp(-1 / (max(dec15, 0.1) * 0.001 * samplerate));\n\n// Higher entropy lifts weaker modes. Higher purity makes excitation more selective.\nexc_shape = mix(0.55, 1.6, pur);\nt0 = pow(sm0 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt1 = pow(sm1 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt2 = pow(sm2 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt3 = pow(sm3 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt4 = pow(sm4 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt5 = pow(sm5 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt6 = pow(sm6 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt7 = pow(sm7 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt8 = pow(sm8 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt9 = pow(sm9 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt10 = pow(sm10 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt11 = pow(sm11 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt12 = pow(sm12 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt13 = pow(sm13 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt14 = pow(sm14 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt15 = pow(sm15 + 0.00001, exc_shape) * mix(0.35, 1, ent);\n\ne0 = (t0 > e0) * (t0 + atk_coeff * (e0 - t0)) + (t0 <= e0) * (t0 + dc0 * (e0 - t0));\ne1 = (t1 > e1) * (t1 + atk_coeff * (e1 - t1)) + (t1 <= e1) * (t1 + dc1 * (e1 - t1));\ne2 = (t2 > e2) * (t2 + atk_coeff * (e2 - t2)) + (t2 <= e2) * (t2 + dc2 * (e2 - t2));\ne3 = (t3 > e3) * (t3 + atk_coeff * (e3 - t3)) + (t3 <= e3) * (t3 + dc3 * (e3 - t3));\ne4 = (t4 > e4) * (t4 + atk_coeff * (e4 - t4)) + (t4 <= e4) * (t4 + dc4 * (e4 - t4));\ne5 = (t5 > e5) * (t5 + atk_coeff * (e5 - t5)) + (t5 <= e5) * (t5 + dc5 * (e5 - t5));\ne6 = (t6 > e6) * (t6 + atk_coeff * (e6 - t6)) + (t6 <= e6) * (t6 + dc6 * (e6 - t6));\ne7 = (t7 > e7) * (t7 + atk_coeff * (e7 - t7)) + (t7 <= e7) * (t7 + dc7 * (e7 - t7));\ne8 = (t8 > e8) * (t8 + atk_coeff * (e8 - t8)) + (t8 <= e8) * (t8 + dc8 * (e8 - t8));\ne9 = (t9 > e9) * (t9 + atk_coeff * (e9 - t9)) + (t9 <= e9) * (t9 + dc9 * (e9 - t9));\ne10 = (t10 > e10) * (t10 + atk_coeff * (e10 - t10)) + (t10 <= e10) * (t10 + dc10 * (e10 - t10));\ne11 = (t11 > e11) * (t11 + atk_coeff * (e11 - t11)) + (t11 <= e11) * (t11 + dc11 * (e11 - t11));\ne12 = (t12 > e12) * (t12 + atk_coeff * (e12 - t12)) + (t12 <= e12) * (t12 + dc12 * (e12 - t12));\ne13 = (t13 > e13) * (t13 + atk_coeff * (e13 - t13)) + (t13 <= e13) * (t13 + dc13 * (e13 - t13));\ne14 = (t14 > e14) * (t14 + atk_coeff * (e14 - t14)) + (t14 <= e14) * (t14 + dc14 * (e14 - t14));\ne15 = (t15 > e15) * (t15 + atk_coeff * (e15 - t15)) + (t15 <= e15) * (t15 + dc15 * (e15 - t15));\n\nbright = clamp(brightness + ent * 0.25, 0, 1);\n\np0 = fract(p0 + freq * max(h0, 0.01) / samplerate);\np1 = fract(p1 + freq * max(h1, 0.01) / samplerate);\np2 = fract(p2 + freq * max(h2, 0.01) / samplerate);\np3 = fract(p3 + freq * max(h3, 0.01) / samplerate);\np4 = fract(p4 + freq * max(h4, 0.01) / samplerate);\np5 = fract(p5 + freq * max(h5, 0.01) / samplerate);\np6 = fract(p6 + freq * max(h6, 0.01) / samplerate);\np7 = fract(p7 + freq * max(h7, 0.01) / samplerate);\np8 = fract(p8 + freq * max(h8, 0.01) / samplerate);\np9 = fract(p9 + freq * max(h9, 0.01) / samplerate);\np10 = fract(p10 + freq * max(h10, 0.01) / samplerate);\np11 = fract(p11 + freq * max(h11, 0.01) / samplerate);\np12 = fract(p12 + freq * max(h12, 0.01) / samplerate);\np13 = fract(p13 + freq * max(h13, 0.01) / samplerate);\np14 = fract(p14 + freq * max(h14, 0.01) / samplerate);\np15 = fract(p15 + freq * max(h15, 0.01) / samplerate);\n\ntwopi = 6.283185307179586;\npartials =\n    e0 * sin(twopi * p0 + sph0) / pow(max(h0, 1), bright) +\n    e1 * sin(twopi * p1 + sph1) / pow(max(h1, 1), bright) +\n    e2 * sin(twopi * p2 + sph2) / pow(max(h2, 1), bright) +\n    e3 * sin(twopi * p3 + sph3) / pow(max(h3, 1), bright) +\n    e4 * sin(twopi * p4 + sph4) / pow(max(h4, 1), bright) +\n    e5 * sin(twopi * p5 + sph5) / pow(max(h5, 1), bright) +\n    e6 * sin(twopi * p6 + sph6) / pow(max(h6, 1), bright) +\n    e7 * sin(twopi * p7 + sph7) / pow(max(h7, 1), bright) +\n    e8 * sin(twopi * p8 + sph8) / pow(max(h8, 1), bright) +\n    e9 * sin(twopi * p9 + sph9) / pow(max(h9, 1), bright) +\n    e10 * sin(twopi * p10 + sph10) / pow(max(h10, 1), bright) +\n    e11 * sin(twopi * p11 + sph11) / pow(max(h11, 1), bright) +\n    e12 * sin(twopi * p12 + sph12) / pow(max(h12, 1), bright) +\n    e13 * sin(twopi * p13 + sph13) / pow(max(h13, 1), bright) +\n    e14 * sin(twopi * p14 + sph14) / pow(max(h14, 1), bright) +\n    e15 * sin(twopi * p15 + sph15) / pow(max(h15, 1), bright);\n\nvoice_scale = 1 / sqrt(max(mix_voices, 1));\nsig = tanh(partials * 0.5);\n\nout1 = sig * amp * output_ceiling * voice_scale;\nout2 = e0 + e1 + e2 + e3 + e4 + e5 + e6 + e7 + e8 + e9 + e10 + e11 + e12 + e13 + e14 + e15;\nout3 = freq;\n",
					"fontface" : 0,
					"fontname" : "<Monospaced>",
					"fontsize" : 12.0,
					"id" : "obj-85",
					"maxclass" : "gen.codebox~",
					"numinlets" : 1,
					"numoutlets" : 3,
					"outlettype" : [ "signal", "signal", "signal" ],
					"patching_rect" : [ 392.000011682510376, 498.666681528091431, 136.000004053115845, 34.666667699813843 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-74",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 921.0, 314.5, 31.0, 22.0 ],
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
					"patching_rect" : [ 919.0, 271.5, 50.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-61",
					"maxclass" : "newobj",
					"numinlets" : 5,
					"numoutlets" : 4,
					"outlettype" : [ "", "", "", "" ],
					"patching_rect" : [ 392.000011682510376, 397.333345174789429, 222.0, 22.0 ],
					"saved_object_attributes" : 					{
						"filename" : "qmw_density_field_to_gen_qvoices.js",
						"parameter_enable" : 0
					}
,
					"text" : "js qmw_density_field_to_gen_qvoices.js"
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
					"patching_rect" : [ 503.0, 646.0, 50.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-57",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 396.0, 672.0, 34.0, 22.0 ],
					"text" : "*~ 1."
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-44",
					"maxclass" : "ezdac~",
					"numinlets" : 2,
					"numoutlets" : 0,
					"patching_rect" : [ 824.000024557113647, 942.666694760322571, 45.0, 45.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-33",
					"maxclass" : "multislider",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 581.333350658416748, 247.666661739349365, 85.0, 83.0 ],
					"size" : 16
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-31",
					"maxclass" : "multislider",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 482.666681051254272, 247.666661739349365, 85.0, 83.0 ],
					"setminmax" : [ 0.0, 1.0 ],
					"size" : 16
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-29",
					"maxclass" : "multislider",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 386.666678190231323, 243.666661620140076, 85.0, 83.0 ],
					"size" : 16
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-28",
					"maxclass" : "multislider",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 277.333341598510742, 243.666661620140076, 85.0, 83.0 ],
					"size" : 16
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-27",
					"maxclass" : "multislider",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 136.000004053115845, 239.666661500930786, 85.0, 83.0 ],
					"setminmax" : [ 0.0, 2.0 ],
					"size" : 16
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-26",
					"maxclass" : "multislider",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 537.333349347114563, 159.666659116744995, 85.0, 83.0 ],
					"size" : 16
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-25",
					"maxclass" : "multislider",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 424.000012636184692, 159.666659116744995, 85.0, 83.0 ],
					"size" : 16
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-24",
					"maxclass" : "multislider",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 277.333341598510742, 151.666658878326416, 85.0, 83.0 ],
					"setminmax" : [ 0.0, 1.0 ],
					"size" : 16
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-23",
					"maxclass" : "multislider",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 136.000004053115845, 151.666658878326416, 85.0, 83.0 ],
					"setminmax" : [ 0.0, 1.0 ],
					"size" : 16
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
					"numoutlets" : 10,
					"outlettype" : [ "", "", "", "", "", "", "", "", "", "" ],
					"patching_rect" : [ 213.333339691162109, 114.333324432373047, 329.0, 22.0 ],
					"text" : "OSC-route /x /y /vx /vy /speed /real /imag /magnitude /phase"
				}

			}
 ],
		"lines" : [ 			{
				"patchline" : 				{
					"destination" : [ "obj-10", 0 ],
					"order" : 0,
					"source" : [ "obj-1", 8 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-23", 0 ],
					"source" : [ "obj-1", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-24", 0 ],
					"source" : [ "obj-1", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-25", 0 ],
					"source" : [ "obj-1", 2 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-26", 0 ],
					"source" : [ "obj-1", 3 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-27", 0 ],
					"order" : 1,
					"source" : [ "obj-1", 4 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-28", 0 ],
					"order" : 1,
					"source" : [ "obj-1", 5 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-29", 0 ],
					"order" : 1,
					"source" : [ "obj-1", 6 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-31", 0 ],
					"order" : 0,
					"source" : [ "obj-1", 7 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-33", 0 ],
					"order" : 1,
					"source" : [ "obj-1", 8 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-5", 0 ],
					"order" : 1,
					"source" : [ "obj-1", 7 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-6", 0 ],
					"order" : 0,
					"source" : [ "obj-1", 5 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-7", 0 ],
					"order" : 0,
					"source" : [ "obj-1", 6 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-8", 0 ],
					"order" : 0,
					"source" : [ "obj-1", 4 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-61", 4 ],
					"source" : [ "obj-10", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-18", 0 ],
					"source" : [ "obj-17", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-85", 0 ],
					"source" : [ "obj-18", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-85", 0 ],
					"source" : [ "obj-19", 0 ]
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
					"destination" : [ "obj-19", 0 ],
					"source" : [ "obj-20", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-32", 0 ],
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
					"destination" : [ "obj-38", 0 ],
					"order" : 1,
					"source" : [ "obj-32", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-44", 1 ],
					"order" : 0,
					"source" : [ "obj-32", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-22", 0 ],
					"source" : [ "obj-34", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-34", 0 ],
					"source" : [ "obj-35", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-22", 0 ],
					"source" : [ "obj-36", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-36", 0 ],
					"source" : [ "obj-37", 0 ]
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
					"destination" : [ "obj-44", 0 ],
					"order" : 1,
					"source" : [ "obj-41", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-48", 0 ],
					"order" : 0,
					"source" : [ "obj-41", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-41", 0 ],
					"source" : [ "obj-42", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-42", 0 ],
					"source" : [ "obj-43", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-43", 0 ],
					"source" : [ "obj-45", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-42", 0 ],
					"source" : [ "obj-46", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-46", 0 ],
					"source" : [ "obj-47", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-61", 2 ],
					"source" : [ "obj-5", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-51", 1 ],
					"source" : [ "obj-50", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-44", 1 ],
					"order" : 1,
					"source" : [ "obj-51", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-49", 0 ],
					"order" : 0,
					"source" : [ "obj-51", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-51", 0 ],
					"source" : [ "obj-52", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-52", 0 ],
					"source" : [ "obj-53", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-53", 0 ],
					"source" : [ "obj-54", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-52", 0 ],
					"source" : [ "obj-55", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-55", 0 ],
					"source" : [ "obj-56", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-11", 0 ],
					"order" : 1,
					"source" : [ "obj-57", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-44", 0 ],
					"order" : 0,
					"source" : [ "obj-57", 0 ]
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
					"destination" : [ "obj-61", 0 ],
					"source" : [ "obj-6", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-22", 0 ],
					"source" : [ "obj-61", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-42", 0 ],
					"source" : [ "obj-61", 2 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-52", 0 ],
					"source" : [ "obj-61", 3 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-85", 0 ],
					"source" : [ "obj-61", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-61", 1 ],
					"source" : [ "obj-7", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-85", 0 ],
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
					"destination" : [ "obj-61", 3 ],
					"source" : [ "obj-8", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-57", 0 ],
					"source" : [ "obj-85", 0 ]
				}

			}
 ],
		"originid" : "pat-6",
		"dependency_cache" : [ 			{
				"name" : "OSC-route.mxo",
				"type" : "iLaX"
			}
, 			{
				"name" : "qmw_density_field_to_gen_qvoices.js",
				"bootpath" : "~/QuantumSonification/max/patches",
				"patcherrelativepath" : ".",
				"type" : "TEXT",
				"implicit" : 1
			}
 ],
		"autosave" : 0
	}

}
