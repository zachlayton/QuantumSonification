{
  "patcher": {
    "fileversion": 1,
    "appversion": {
      "major": 9,
      "minor": 0,
      "revision": 5,
      "architecture": "x64",
      "modernui": 1
    },
    "classnamespace": "box",
    "rect": [
      34,
      100,
      1444,
      950
    ],
    "openinpresentation": 1,
    "gridsize": [
      15,
      15
    ],
    "boxes": [
      {
        "box": {
          "fontsize": 18,
          "id": "obj-1",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            20,
            15,
            690,
            27
          ],
          "presentation": 1,
          "presentation_rect": [
            20,
            15,
            720,
            27
          ],
          "text": "BLOCH SPHERE → GENEXPR RESONATOR + CONVOLUTION IR + SPAT5 v5"
        }
      },
      {
        "box": {
          "id": "obj-2",
          "linecount": 2,
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            20,
            43,
            732,
            33
          ],
          "presentation": 1,
          "presentation_linecount": 2,
          "presentation_rect": [
            20,
            43,
            730,
            33
          ],
          "text": "Density-engine OSC drives the Bloch direction; Yℓm excites the canonical GenExpr resonator; a portable dual-geometry convolution stage morphs between Tanglecube and Heart impulse responses."
        }
      },
      {
        "box": {
          "disablefind": 0,
          "id": "obj-3",
          "maxclass": "jweb",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            20,
            90,
            740,
            720
          ],
          "presentation": 1,
          "presentation_rect": [
            20,
            90,
            740,
            720
          ],
          "rendermode": 0,
          "url": "file://bloch-harmonics-max-direct.html"
        }
      },
      {
        "box": {
          "id": "obj-4",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "bang"
          ],
          "patching_rect": [
            800,
            720,
            60,
            22
          ],
          "text": "loadbang"
        }
      },
      {
        "box": {
          "id": "obj-5",
          "maxclass": "message",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            800,
            750,
            225,
            22
          ],
          "text": "readfile bloch-harmonics-max-direct.html"
        }
      },
      {
        "box": {
          "id": "obj-6",
          "maxclass": "newobj",
          "numinlets": 2,
          "numoutlets": 2,
          "outlettype": [
            "",
            ""
          ],
          "patching_rect": [
            800,
            90,
            120,
            22
          ],
          "text": "route maxmessage"
        }
      },
      {
        "box": {
          "id": "obj-7",
          "maxclass": "newobj",
          "numinlets": 2,
          "numoutlets": 2,
          "outlettype": [
            "",
            ""
          ],
          "patching_rect": [
            800,
            120,
            80,
            22
          ],
          "text": "route state"
        }
      },
      {
        "box": {
          "id": "obj-8",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 20,
          "outlettype": [
            "float",
            "float",
            "float",
            "float",
            "float",
            "float",
            "float",
            "float",
            "float",
            "float",
            "float",
            "float",
            "float",
            "float",
            "float",
            "float",
            "float",
            "float",
            "float",
            "float"
          ],
          "patching_rect": [
            800,
            150,
            570,
            22
          ],
          "text": "unpack f f f f f f f f f f f f f f f f f f f f"
        }
      },
      {
        "box": {
          "id": "obj-9",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            790,
            205,
            100,
            20
          ],
          "presentation": 1,
          "presentation_rect": [
            790,
            110,
            110,
            20
          ],
          "text": "θ (degrees)"
        }
      },
      {
        "box": {
          "format": 6,
          "id": "obj-10",
          "maxclass": "flonum",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "",
            "bang"
          ],
          "parameter_enable": 0,
          "patching_rect": [
            900,
            200,
            95,
            22
          ],
          "presentation": 1,
          "presentation_rect": [
            900,
            105,
            95,
            22
          ]
        }
      },
      {
        "box": {
          "id": "obj-11",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            790,
            259,
            100,
            20
          ],
          "presentation": 1,
          "presentation_rect": [
            790,
            164,
            110,
            20
          ],
          "text": "φ (degrees)"
        }
      },
      {
        "box": {
          "format": 6,
          "id": "obj-12",
          "maxclass": "flonum",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "",
            "bang"
          ],
          "parameter_enable": 0,
          "patching_rect": [
            900,
            254,
            95,
            22
          ],
          "presentation": 1,
          "presentation_rect": [
            900,
            159,
            95,
            22
          ]
        }
      },
      {
        "box": {
          "id": "obj-13",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            790,
            313,
            100,
            20
          ],
          "presentation": 1,
          "presentation_rect": [
            790,
            218,
            110,
            20
          ],
          "text": "Bloch X"
        }
      },
      {
        "box": {
          "format": 6,
          "id": "obj-14",
          "maxclass": "flonum",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "",
            "bang"
          ],
          "parameter_enable": 0,
          "patching_rect": [
            900,
            308,
            95,
            22
          ],
          "presentation": 1,
          "presentation_rect": [
            900,
            213,
            95,
            22
          ]
        }
      },
      {
        "box": {
          "id": "obj-15",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            790,
            367,
            100,
            20
          ],
          "presentation": 1,
          "presentation_rect": [
            790,
            272,
            110,
            20
          ],
          "text": "Bloch Y"
        }
      },
      {
        "box": {
          "format": 6,
          "id": "obj-16",
          "maxclass": "flonum",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "",
            "bang"
          ],
          "parameter_enable": 0,
          "patching_rect": [
            900,
            362,
            95,
            22
          ],
          "presentation": 1,
          "presentation_rect": [
            900,
            267,
            95,
            22
          ]
        }
      },
      {
        "box": {
          "id": "obj-17",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            790,
            421,
            100,
            20
          ],
          "presentation": 1,
          "presentation_rect": [
            790,
            326,
            110,
            20
          ],
          "text": "Bloch Z"
        }
      },
      {
        "box": {
          "format": 6,
          "id": "obj-18",
          "maxclass": "flonum",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "",
            "bang"
          ],
          "parameter_enable": 0,
          "patching_rect": [
            900,
            416,
            95,
            22
          ],
          "presentation": 1,
          "presentation_rect": [
            900,
            321,
            95,
            22
          ]
        }
      },
      {
        "box": {
          "fontsize": 14,
          "id": "obj-19",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            790,
            175,
            260,
            22
          ],
          "presentation": 1,
          "presentation_rect": [
            790,
            80,
            280,
            22
          ],
          "text": "Live state from the animation"
        }
      },
      {
        "box": {
          "fontsize": 14,
          "id": "obj-120",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            790,
            640,
            220,
            22
          ],
          "presentation": 1,
          "presentation_rect": [
            790,
            625,
            240,
            22
          ],
          "text": "GenExpr mapping"
        }
      },
      {
        "box": {
          "id": "obj-121",
          "linecount": 4,
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            790,
            670,
            583,
            33
          ],
          "presentation": 1,
          "presentation_linecount": 2,
          "presentation_rect": [
            790,
            655,
            225,
            74
          ],
          "text": "|Yℓm| → resonator magnitude  •  sign(Yℓm) → 0/π phase  •  degree sets decay speed\\nThe first 15 resonant lanes follow the visible bars; lane 16 remains reserved."
        }
      },
      {
        "box": {
          "id": "obj-122",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            790,
            730,
            500,
            20
          ],
          "presentation": 1,
          "presentation_rect": [
            790,
            775,
            520,
            22
          ],
          "text": "Runtime assets and both stereo IR files must remain beside this patch.",
          "textcolor": [
            0.45,
            0.45,
            0.45,
            1
          ]
        }
      },
      {
        "box": {
          "id": "obj-123",
          "maxclass": "newobj",
          "numinlets": 2,
          "numoutlets": 2,
          "outlettype": [
            "",
            ""
          ],
          "patching_rect": [
            940,
            90,
            75,
            22
          ],
          "text": "route state"
        }
      },
      {
        "box": {
          "id": "obj-124",
          "maxclass": "button",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "bang"
          ],
          "parameter_enable": 0,
          "patching_rect": [
            1030,
            90,
            24,
            24
          ],
          "presentation": 1,
          "presentation_rect": [
            1030,
            80,
            24,
            24
          ]
        }
      },
      {
        "box": {
          "id": "obj-125",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            1060,
            92,
            160,
            20
          ],
          "presentation": 1,
          "presentation_rect": [
            1060,
            82,
            180,
            20
          ],
          "text": "harmonic bridge activity"
        }
      },
      {
        "box": {
          "code": "// QMW Density Field Quantum Resonator 16\n//\n// Gen~ codebox.\n// in1 is the carrier frequency in Hz.\n// m0..m15 excite sixteen resonant partials.\n// ph0..ph15 set smoothed per-partial timing/phase.\n// s0..s15 set lifetime: fast lanes flash, slow lanes ring.\n// h0..h15 are partial ratios. Defaults are harmonic 1..16, but these can\n// later be replaced by Hamiltonian energy-gap ratios.\n\nParam m0(0);\nParam m1(0);\nParam m2(0);\nParam m3(0);\nParam m4(0);\nParam m5(0);\nParam m6(0);\nParam m7(0);\nParam m8(0);\nParam m9(0);\nParam m10(0);\nParam m11(0);\nParam m12(0);\nParam m13(0);\nParam m14(0);\nParam m15(0);\n\nParam ph0(0);\nParam ph1(0);\nParam ph2(0);\nParam ph3(0);\nParam ph4(0);\nParam ph5(0);\nParam ph6(0);\nParam ph7(0);\nParam ph8(0);\nParam ph9(0);\nParam ph10(0);\nParam ph11(0);\nParam ph12(0);\nParam ph13(0);\nParam ph14(0);\nParam ph15(0);\n\nParam s0(0);\nParam s1(0);\nParam s2(0);\nParam s3(0);\nParam s4(0);\nParam s5(0);\nParam s6(0);\nParam s7(0);\nParam s8(0);\nParam s9(0);\nParam s10(0);\nParam s11(0);\nParam s12(0);\nParam s13(0);\nParam s14(0);\nParam s15(0);\n\nParam h0(1);\nParam h1(2);\nParam h2(3);\nParam h3(4);\nParam h4(5);\nParam h5(6);\nParam h6(7);\nParam h7(8);\nParam h8(9);\nParam h9(10);\nParam h10(11);\nParam h11(12);\nParam h12(13);\nParam h13(14);\nParam h14(15);\nParam h15(16);\n\nParam purity(1);\nParam entropy(0);\nParam coherence(0);\nParam amp(0.2);\nParam default_freq(55);\nParam attack_ms(12);\nParam slow_decay_ms(900);\nParam fast_decay_ms(70);\nParam phase_smooth_ms(100);\nParam magnitude_smooth_ms(100);\nParam brightness(0.65);\nParam mix_voices(4);\nParam output_ceiling(0.85);\n\nHistory p0(0);\nHistory p1(0);\nHistory p2(0);\nHistory p3(0);\nHistory p4(0);\nHistory p5(0);\nHistory p6(0);\nHistory p7(0);\nHistory p8(0);\nHistory p9(0);\nHistory p10(0);\nHistory p11(0);\nHistory p12(0);\nHistory p13(0);\nHistory p14(0);\nHistory p15(0);\n\nHistory e0(0);\nHistory e1(0);\nHistory e2(0);\nHistory e3(0);\nHistory e4(0);\nHistory e5(0);\nHistory e6(0);\nHistory e7(0);\nHistory e8(0);\nHistory e9(0);\nHistory e10(0);\nHistory e11(0);\nHistory e12(0);\nHistory e13(0);\nHistory e14(0);\nHistory e15(0);\n\nHistory sm0(0);\nHistory sm1(0);\nHistory sm2(0);\nHistory sm3(0);\nHistory sm4(0);\nHistory sm5(0);\nHistory sm6(0);\nHistory sm7(0);\nHistory sm8(0);\nHistory sm9(0);\nHistory sm10(0);\nHistory sm11(0);\nHistory sm12(0);\nHistory sm13(0);\nHistory sm14(0);\nHistory sm15(0);\n\nHistory sph0(0);\nHistory sph1(0);\nHistory sph2(0);\nHistory sph3(0);\nHistory sph4(0);\nHistory sph5(0);\nHistory sph6(0);\nHistory sph7(0);\nHistory sph8(0);\nHistory sph9(0);\nHistory sph10(0);\nHistory sph11(0);\nHistory sph12(0);\nHistory sph13(0);\nHistory sph14(0);\nHistory sph15(0);\n\nfreq = (in1 > 0) * in1 + (in1 <= 0) * default_freq;\npur = clamp(purity, 0, 1);\nent = clamp(entropy, 0, 1);\ncoh = clamp(coherence, 0, 1);\n\nmag_ms = max(magnitude_smooth_ms, 0.1);\nmag_coeff = exp(-1 / (mag_ms * 0.001 * samplerate));\n\ntm0 = clamp(m0, 0, 1);\ntm1 = clamp(m1, 0, 1);\ntm2 = clamp(m2, 0, 1);\ntm3 = clamp(m3, 0, 1);\ntm4 = clamp(m4, 0, 1);\ntm5 = clamp(m5, 0, 1);\ntm6 = clamp(m6, 0, 1);\ntm7 = clamp(m7, 0, 1);\ntm8 = clamp(m8, 0, 1);\ntm9 = clamp(m9, 0, 1);\ntm10 = clamp(m10, 0, 1);\ntm11 = clamp(m11, 0, 1);\ntm12 = clamp(m12, 0, 1);\ntm13 = clamp(m13, 0, 1);\ntm14 = clamp(m14, 0, 1);\ntm15 = clamp(m15, 0, 1);\n\nsm0 = tm0 + mag_coeff * (sm0 - tm0);\nsm1 = tm1 + mag_coeff * (sm1 - tm1);\nsm2 = tm2 + mag_coeff * (sm2 - tm2);\nsm3 = tm3 + mag_coeff * (sm3 - tm3);\nsm4 = tm4 + mag_coeff * (sm4 - tm4);\nsm5 = tm5 + mag_coeff * (sm5 - tm5);\nsm6 = tm6 + mag_coeff * (sm6 - tm6);\nsm7 = tm7 + mag_coeff * (sm7 - tm7);\nsm8 = tm8 + mag_coeff * (sm8 - tm8);\nsm9 = tm9 + mag_coeff * (sm9 - tm9);\nsm10 = tm10 + mag_coeff * (sm10 - tm10);\nsm11 = tm11 + mag_coeff * (sm11 - tm11);\nsm12 = tm12 + mag_coeff * (sm12 - tm12);\nsm13 = tm13 + mag_coeff * (sm13 - tm13);\nsm14 = tm14 + mag_coeff * (sm14 - tm14);\nsm15 = tm15 + mag_coeff * (sm15 - tm15);\n\nphase_ms = max(phase_smooth_ms, 0.1);\nphase_coeff = exp(-1 / (phase_ms * 0.001 * samplerate));\n\ndph0 = atan2(sin(ph0 - sph0), cos(ph0 - sph0));\ndph1 = atan2(sin(ph1 - sph1), cos(ph1 - sph1));\ndph2 = atan2(sin(ph2 - sph2), cos(ph2 - sph2));\ndph3 = atan2(sin(ph3 - sph3), cos(ph3 - sph3));\ndph4 = atan2(sin(ph4 - sph4), cos(ph4 - sph4));\ndph5 = atan2(sin(ph5 - sph5), cos(ph5 - sph5));\ndph6 = atan2(sin(ph6 - sph6), cos(ph6 - sph6));\ndph7 = atan2(sin(ph7 - sph7), cos(ph7 - sph7));\ndph8 = atan2(sin(ph8 - sph8), cos(ph8 - sph8));\ndph9 = atan2(sin(ph9 - sph9), cos(ph9 - sph9));\ndph10 = atan2(sin(ph10 - sph10), cos(ph10 - sph10));\ndph11 = atan2(sin(ph11 - sph11), cos(ph11 - sph11));\ndph12 = atan2(sin(ph12 - sph12), cos(ph12 - sph12));\ndph13 = atan2(sin(ph13 - sph13), cos(ph13 - sph13));\ndph14 = atan2(sin(ph14 - sph14), cos(ph14 - sph14));\ndph15 = atan2(sin(ph15 - sph15), cos(ph15 - sph15));\n\nsph0 = sph0 + (1 - phase_coeff) * dph0;\nsph1 = sph1 + (1 - phase_coeff) * dph1;\nsph2 = sph2 + (1 - phase_coeff) * dph2;\nsph3 = sph3 + (1 - phase_coeff) * dph3;\nsph4 = sph4 + (1 - phase_coeff) * dph4;\nsph5 = sph5 + (1 - phase_coeff) * dph5;\nsph6 = sph6 + (1 - phase_coeff) * dph6;\nsph7 = sph7 + (1 - phase_coeff) * dph7;\nsph8 = sph8 + (1 - phase_coeff) * dph8;\nsph9 = sph9 + (1 - phase_coeff) * dph9;\nsph10 = sph10 + (1 - phase_coeff) * dph10;\nsph11 = sph11 + (1 - phase_coeff) * dph11;\nsph12 = sph12 + (1 - phase_coeff) * dph12;\nsph13 = sph13 + (1 - phase_coeff) * dph13;\nsph14 = sph14 + (1 - phase_coeff) * dph14;\nsph15 = sph15 + (1 - phase_coeff) * dph15;\n\natk_ms = max(attack_ms * mix(1.35, 0.65, coh), 0.1);\natk_coeff = exp(-1 / (atk_ms * 0.001 * samplerate));\n\nspd0 = clamp(abs(s0), 0, 1);\nspd1 = clamp(abs(s1), 0, 1);\nspd2 = clamp(abs(s2), 0, 1);\nspd3 = clamp(abs(s3), 0, 1);\nspd4 = clamp(abs(s4), 0, 1);\nspd5 = clamp(abs(s5), 0, 1);\nspd6 = clamp(abs(s6), 0, 1);\nspd7 = clamp(abs(s7), 0, 1);\nspd8 = clamp(abs(s8), 0, 1);\nspd9 = clamp(abs(s9), 0, 1);\nspd10 = clamp(abs(s10), 0, 1);\nspd11 = clamp(abs(s11), 0, 1);\nspd12 = clamp(abs(s12), 0, 1);\nspd13 = clamp(abs(s13), 0, 1);\nspd14 = clamp(abs(s14), 0, 1);\nspd15 = clamp(abs(s15), 0, 1);\n\ndec0 = mix(slow_decay_ms, fast_decay_ms, spd0);\ndec1 = mix(slow_decay_ms, fast_decay_ms, spd1);\ndec2 = mix(slow_decay_ms, fast_decay_ms, spd2);\ndec3 = mix(slow_decay_ms, fast_decay_ms, spd3);\ndec4 = mix(slow_decay_ms, fast_decay_ms, spd4);\ndec5 = mix(slow_decay_ms, fast_decay_ms, spd5);\ndec6 = mix(slow_decay_ms, fast_decay_ms, spd6);\ndec7 = mix(slow_decay_ms, fast_decay_ms, spd7);\ndec8 = mix(slow_decay_ms, fast_decay_ms, spd8);\ndec9 = mix(slow_decay_ms, fast_decay_ms, spd9);\ndec10 = mix(slow_decay_ms, fast_decay_ms, spd10);\ndec11 = mix(slow_decay_ms, fast_decay_ms, spd11);\ndec12 = mix(slow_decay_ms, fast_decay_ms, spd12);\ndec13 = mix(slow_decay_ms, fast_decay_ms, spd13);\ndec14 = mix(slow_decay_ms, fast_decay_ms, spd14);\ndec15 = mix(slow_decay_ms, fast_decay_ms, spd15);\n\ndc0 = exp(-1 / (max(dec0, 0.1) * 0.001 * samplerate));\ndc1 = exp(-1 / (max(dec1, 0.1) * 0.001 * samplerate));\ndc2 = exp(-1 / (max(dec2, 0.1) * 0.001 * samplerate));\ndc3 = exp(-1 / (max(dec3, 0.1) * 0.001 * samplerate));\ndc4 = exp(-1 / (max(dec4, 0.1) * 0.001 * samplerate));\ndc5 = exp(-1 / (max(dec5, 0.1) * 0.001 * samplerate));\ndc6 = exp(-1 / (max(dec6, 0.1) * 0.001 * samplerate));\ndc7 = exp(-1 / (max(dec7, 0.1) * 0.001 * samplerate));\ndc8 = exp(-1 / (max(dec8, 0.1) * 0.001 * samplerate));\ndc9 = exp(-1 / (max(dec9, 0.1) * 0.001 * samplerate));\ndc10 = exp(-1 / (max(dec10, 0.1) * 0.001 * samplerate));\ndc11 = exp(-1 / (max(dec11, 0.1) * 0.001 * samplerate));\ndc12 = exp(-1 / (max(dec12, 0.1) * 0.001 * samplerate));\ndc13 = exp(-1 / (max(dec13, 0.1) * 0.001 * samplerate));\ndc14 = exp(-1 / (max(dec14, 0.1) * 0.001 * samplerate));\ndc15 = exp(-1 / (max(dec15, 0.1) * 0.001 * samplerate));\n\n// Higher entropy lifts weaker modes. Higher purity makes excitation more selective.\nexc_shape = mix(0.55, 1.6, pur);\nt0 = pow(sm0 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt1 = pow(sm1 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt2 = pow(sm2 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt3 = pow(sm3 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt4 = pow(sm4 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt5 = pow(sm5 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt6 = pow(sm6 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt7 = pow(sm7 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt8 = pow(sm8 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt9 = pow(sm9 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt10 = pow(sm10 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt11 = pow(sm11 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt12 = pow(sm12 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt13 = pow(sm13 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt14 = pow(sm14 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt15 = pow(sm15 + 0.00001, exc_shape) * mix(0.35, 1, ent);\n\ne0 = (t0 > e0) * (t0 + atk_coeff * (e0 - t0)) + (t0 <= e0) * (t0 + dc0 * (e0 - t0));\ne1 = (t1 > e1) * (t1 + atk_coeff * (e1 - t1)) + (t1 <= e1) * (t1 + dc1 * (e1 - t1));\ne2 = (t2 > e2) * (t2 + atk_coeff * (e2 - t2)) + (t2 <= e2) * (t2 + dc2 * (e2 - t2));\ne3 = (t3 > e3) * (t3 + atk_coeff * (e3 - t3)) + (t3 <= e3) * (t3 + dc3 * (e3 - t3));\ne4 = (t4 > e4) * (t4 + atk_coeff * (e4 - t4)) + (t4 <= e4) * (t4 + dc4 * (e4 - t4));\ne5 = (t5 > e5) * (t5 + atk_coeff * (e5 - t5)) + (t5 <= e5) * (t5 + dc5 * (e5 - t5));\ne6 = (t6 > e6) * (t6 + atk_coeff * (e6 - t6)) + (t6 <= e6) * (t6 + dc6 * (e6 - t6));\ne7 = (t7 > e7) * (t7 + atk_coeff * (e7 - t7)) + (t7 <= e7) * (t7 + dc7 * (e7 - t7));\ne8 = (t8 > e8) * (t8 + atk_coeff * (e8 - t8)) + (t8 <= e8) * (t8 + dc8 * (e8 - t8));\ne9 = (t9 > e9) * (t9 + atk_coeff * (e9 - t9)) + (t9 <= e9) * (t9 + dc9 * (e9 - t9));\ne10 = (t10 > e10) * (t10 + atk_coeff * (e10 - t10)) + (t10 <= e10) * (t10 + dc10 * (e10 - t10));\ne11 = (t11 > e11) * (t11 + atk_coeff * (e11 - t11)) + (t11 <= e11) * (t11 + dc11 * (e11 - t11));\ne12 = (t12 > e12) * (t12 + atk_coeff * (e12 - t12)) + (t12 <= e12) * (t12 + dc12 * (e12 - t12));\ne13 = (t13 > e13) * (t13 + atk_coeff * (e13 - t13)) + (t13 <= e13) * (t13 + dc13 * (e13 - t13));\ne14 = (t14 > e14) * (t14 + atk_coeff * (e14 - t14)) + (t14 <= e14) * (t14 + dc14 * (e14 - t14));\ne15 = (t15 > e15) * (t15 + atk_coeff * (e15 - t15)) + (t15 <= e15) * (t15 + dc15 * (e15 - t15));\n\nbright = clamp(brightness + ent * 0.25, 0, 1);\n\np0 = fract(p0 + freq * max(h0, 0.01) / samplerate);\np1 = fract(p1 + freq * max(h1, 0.01) / samplerate);\np2 = fract(p2 + freq * max(h2, 0.01) / samplerate);\np3 = fract(p3 + freq * max(h3, 0.01) / samplerate);\np4 = fract(p4 + freq * max(h4, 0.01) / samplerate);\np5 = fract(p5 + freq * max(h5, 0.01) / samplerate);\np6 = fract(p6 + freq * max(h6, 0.01) / samplerate);\np7 = fract(p7 + freq * max(h7, 0.01) / samplerate);\np8 = fract(p8 + freq * max(h8, 0.01) / samplerate);\np9 = fract(p9 + freq * max(h9, 0.01) / samplerate);\np10 = fract(p10 + freq * max(h10, 0.01) / samplerate);\np11 = fract(p11 + freq * max(h11, 0.01) / samplerate);\np12 = fract(p12 + freq * max(h12, 0.01) / samplerate);\np13 = fract(p13 + freq * max(h13, 0.01) / samplerate);\np14 = fract(p14 + freq * max(h14, 0.01) / samplerate);\np15 = fract(p15 + freq * max(h15, 0.01) / samplerate);\n\ntwopi = 6.283185307179586;\npartials =\n    e0 * sin(twopi * p0 + sph0) / pow(max(h0, 1), bright) +\n    e1 * sin(twopi * p1 + sph1) / pow(max(h1, 1), bright) +\n    e2 * sin(twopi * p2 + sph2) / pow(max(h2, 1), bright) +\n    e3 * sin(twopi * p3 + sph3) / pow(max(h3, 1), bright) +\n    e4 * sin(twopi * p4 + sph4) / pow(max(h4, 1), bright) +\n    e5 * sin(twopi * p5 + sph5) / pow(max(h5, 1), bright) +\n    e6 * sin(twopi * p6 + sph6) / pow(max(h6, 1), bright) +\n    e7 * sin(twopi * p7 + sph7) / pow(max(h7, 1), bright) +\n    e8 * sin(twopi * p8 + sph8) / pow(max(h8, 1), bright) +\n    e9 * sin(twopi * p9 + sph9) / pow(max(h9, 1), bright) +\n    e10 * sin(twopi * p10 + sph10) / pow(max(h10, 1), bright) +\n    e11 * sin(twopi * p11 + sph11) / pow(max(h11, 1), bright) +\n    e12 * sin(twopi * p12 + sph12) / pow(max(h12, 1), bright) +\n    e13 * sin(twopi * p13 + sph13) / pow(max(h13, 1), bright) +\n    e14 * sin(twopi * p14 + sph14) / pow(max(h14, 1), bright) +\n    e15 * sin(twopi * p15 + sph15) / pow(max(h15, 1), bright);\n\nvoice_scale = 1 / sqrt(max(mix_voices, 1));\nsig = tanh(partials * 0.5);\n\nout1 = sig * amp * output_ceiling * voice_scale;\nout2 = e0 + e1 + e2 + e3 + e4 + e5 + e6 + e7 + e8 + e9 + e10 + e11 + e12 + e13 + e14 + e15;\nout3 = freq;\n",
          "fontface": 0,
          "fontname": "<Monospaced>",
          "fontsize": 12,
          "id": "obj-200",
          "maxclass": "gen.codebox~",
          "numinlets": 1,
          "numoutlets": 3,
          "outlettype": [
            "signal",
            "signal",
            "signal"
          ],
          "patching_rect": [
            674,
            862,
            150,
            60
          ]
        }
      },
      {
        "box": {
          "id": "obj-201",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            790,
            385,
            110,
            20
          ],
          "presentation": 1,
          "presentation_rect": [
            790,
            375,
            110,
            20
          ],
          "text": "Fundamental (Hz)"
        }
      },
      {
        "box": {
          "format": 6,
          "id": "obj-202",
          "maxclass": "flonum",
          "maximum": 1000,
          "minimum": 20,
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "",
            "bang"
          ],
          "parameter_enable": 0,
          "patching_rect": [
            905,
            380,
            85,
            22
          ],
          "presentation": 1,
          "presentation_rect": [
            905,
            370,
            85,
            22
          ]
        }
      },
      {
        "box": {
          "id": "obj-203",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1000,
            380,
            85,
            22
          ],
          "text": "loadmess 55."
        }
      },
      {
        "box": {
          "id": "obj-204",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ],
          "patching_rect": [
            1095,
            380,
            38,
            22
          ],
          "text": "sig~"
        }
      },
      {
        "box": {
          "id": "obj-205",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            790,
            420,
            110,
            20
          ],
          "presentation": 1,
          "presentation_rect": [
            790,
            410,
            110,
            20
          ],
          "text": "Spectral tilt trim"
        }
      },
      {
        "box": {
          "format": 6,
          "id": "obj-206",
          "maxclass": "flonum",
          "maximum": 0.5,
          "minimum": -0.5,
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "",
            "bang"
          ],
          "parameter_enable": 0,
          "patching_rect": [
            905,
            415,
            85,
            22
          ],
          "presentation": 1,
          "presentation_rect": [
            905,
            405,
            85,
            22
          ]
        }
      },
      {
        "box": {
          "id": "obj-207",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1000,
            415,
            140,
            22
          ],
          "text": "prepend brightness"
        }
      },
      {
        "box": {
          "id": "obj-208",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1150,
            415,
            95,
            22
          ],
          "text": "loadmess 0."
        }
      },
      {
        "box": {
          "id": "obj-209",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            790,
            455,
            110,
            20
          ],
          "presentation": 1,
          "presentation_rect": [
            790,
            445,
            110,
            20
          ],
          "text": "Purity"
        }
      },
      {
        "box": {
          "format": 6,
          "id": "obj-210",
          "maxclass": "flonum",
          "maximum": 1,
          "minimum": 0,
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "",
            "bang"
          ],
          "parameter_enable": 0,
          "patching_rect": [
            905,
            450,
            85,
            22
          ],
          "presentation": 1,
          "presentation_rect": [
            905,
            440,
            85,
            22
          ]
        }
      },
      {
        "box": {
          "id": "obj-211",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1000,
            450,
            140,
            22
          ],
          "text": "prepend purity"
        }
      },
      {
        "box": {
          "id": "obj-212",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1150,
            450,
            95,
            22
          ],
          "text": "loadmess 1"
        }
      },
      {
        "box": {
          "id": "obj-213",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            790,
            490,
            110,
            20
          ],
          "presentation": 1,
          "presentation_rect": [
            790,
            480,
            110,
            20
          ],
          "text": "Entropy"
        }
      },
      {
        "box": {
          "format": 6,
          "id": "obj-214",
          "maxclass": "flonum",
          "maximum": 1,
          "minimum": 0,
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "",
            "bang"
          ],
          "parameter_enable": 0,
          "patching_rect": [
            905,
            485,
            85,
            22
          ],
          "presentation": 1,
          "presentation_rect": [
            905,
            475,
            85,
            22
          ]
        }
      },
      {
        "box": {
          "id": "obj-215",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1000,
            485,
            140,
            22
          ],
          "text": "prepend entropy"
        }
      },
      {
        "box": {
          "id": "obj-216",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1150,
            485,
            95,
            22
          ],
          "text": "loadmess 0.12"
        }
      },
      {
        "box": {
          "id": "obj-217",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            790,
            525,
            110,
            20
          ],
          "presentation": 1,
          "presentation_rect": [
            790,
            515,
            110,
            20
          ],
          "text": "Coherence"
        }
      },
      {
        "box": {
          "format": 6,
          "id": "obj-218",
          "maxclass": "flonum",
          "maximum": 1,
          "minimum": 0,
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "",
            "bang"
          ],
          "parameter_enable": 0,
          "patching_rect": [
            905,
            520,
            85,
            22
          ],
          "presentation": 1,
          "presentation_rect": [
            905,
            510,
            85,
            22
          ]
        }
      },
      {
        "box": {
          "id": "obj-219",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1000,
            520,
            140,
            22
          ],
          "text": "prepend coherence"
        }
      },
      {
        "box": {
          "id": "obj-220",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1150,
            520,
            95,
            22
          ],
          "text": "loadmess 0.7"
        }
      },
      {
        "box": {
          "id": "obj-221",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            790,
            560,
            110,
            20
          ],
          "presentation": 1,
          "presentation_rect": [
            790,
            550,
            110,
            20
          ],
          "text": "Slow decay (ms)"
        }
      },
      {
        "box": {
          "format": 6,
          "id": "obj-222",
          "maxclass": "flonum",
          "maximum": 5000,
          "minimum": 100,
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "",
            "bang"
          ],
          "parameter_enable": 0,
          "patching_rect": [
            905,
            555,
            85,
            22
          ],
          "presentation": 1,
          "presentation_rect": [
            905,
            545,
            85,
            22
          ]
        }
      },
      {
        "box": {
          "id": "obj-223",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1000,
            555,
            141,
            22
          ],
          "text": "prepend slow_decay_ms"
        }
      },
      {
        "box": {
          "id": "obj-224",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1150,
            555,
            95,
            22
          ],
          "text": "loadmess 1200"
        }
      },
      {
        "box": {
          "id": "obj-225",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            790,
            595,
            110,
            20
          ],
          "presentation": 1,
          "presentation_rect": [
            790,
            585,
            110,
            20
          ],
          "text": "Fast decay (ms)"
        }
      },
      {
        "box": {
          "format": 6,
          "id": "obj-226",
          "maxclass": "flonum",
          "maximum": 1000,
          "minimum": 10,
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "",
            "bang"
          ],
          "parameter_enable": 0,
          "patching_rect": [
            905,
            590,
            85,
            22
          ],
          "presentation": 1,
          "presentation_rect": [
            905,
            580,
            85,
            22
          ]
        }
      },
      {
        "box": {
          "id": "obj-227",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1000,
            590,
            140,
            22
          ],
          "text": "prepend fast_decay_ms"
        }
      },
      {
        "box": {
          "id": "obj-228",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1150,
            590,
            95,
            22
          ],
          "text": "loadmess 90"
        }
      },
      {
        "box": {
          "id": "obj-229",
          "linecount": 2,
          "maxclass": "message",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            800,
            800,
            390,
            35
          ],
          "text": "s0 0.18, s1 0.18, s2 0.18, s3 0.42, s4 0.42, s5 0.42, s6 0.42, s7 0.42, s8 0.72, s9 0.72, s10 0.72, s11 0.72, s12 0.72, s13 0.72, s14 0.72, s15 0.9"
        }
      },
      {
        "box": {
          "id": "obj-230",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ],
          "patching_rect": [
            800,
            670,
            48,
            22
          ],
          "text": "abs 0."
        }
      },
      {
        "box": {
          "id": "obj-231",
          "maxclass": "newobj",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ],
          "patching_rect": [
            800,
            697,
            48,
            22
          ],
          "text": "* 1.6"
        }
      },
      {
        "box": {
          "id": "obj-232",
          "maxclass": "newobj",
          "numinlets": 3,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            800,
            724,
            72,
            22
          ],
          "text": "clip 0. 1."
        }
      },
      {
        "box": {
          "id": "obj-233",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            800,
            751,
            82,
            22
          ],
          "text": "prepend m0"
        }
      },
      {
        "box": {
          "id": "obj-234",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            886,
            670,
            155,
            22
          ],
          "text": "expr ($f1 < 0.) * 3.141593"
        }
      },
      {
        "box": {
          "id": "obj-235",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            886,
            697,
            90,
            22
          ],
          "text": "prepend ph0"
        }
      },
      {
        "box": {
          "id": "obj-236",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ],
          "patching_rect": [
            950,
            670,
            48,
            22
          ],
          "text": "abs 0."
        }
      },
      {
        "box": {
          "id": "obj-237",
          "maxclass": "newobj",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ],
          "patching_rect": [
            950,
            697,
            48,
            22
          ],
          "text": "* 1.6"
        }
      },
      {
        "box": {
          "id": "obj-238",
          "maxclass": "newobj",
          "numinlets": 3,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            950,
            724,
            72,
            22
          ],
          "text": "clip 0. 1."
        }
      },
      {
        "box": {
          "id": "obj-239",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            950,
            751,
            82,
            22
          ],
          "text": "prepend m1"
        }
      },
      {
        "box": {
          "id": "obj-240",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1036,
            670,
            155,
            22
          ],
          "text": "expr ($f1 < 0.) * 3.141593"
        }
      },
      {
        "box": {
          "id": "obj-241",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1036,
            697,
            90,
            22
          ],
          "text": "prepend ph1"
        }
      },
      {
        "box": {
          "id": "obj-242",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ],
          "patching_rect": [
            1100,
            670,
            48,
            22
          ],
          "text": "abs 0."
        }
      },
      {
        "box": {
          "id": "obj-243",
          "maxclass": "newobj",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ],
          "patching_rect": [
            1100,
            697,
            48,
            22
          ],
          "text": "* 1.6"
        }
      },
      {
        "box": {
          "id": "obj-244",
          "maxclass": "newobj",
          "numinlets": 3,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1100,
            724,
            72,
            22
          ],
          "text": "clip 0. 1."
        }
      },
      {
        "box": {
          "id": "obj-245",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1100,
            751,
            82,
            22
          ],
          "text": "prepend m2"
        }
      },
      {
        "box": {
          "id": "obj-246",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1186,
            670,
            155,
            22
          ],
          "text": "expr ($f1 < 0.) * 3.141593"
        }
      },
      {
        "box": {
          "id": "obj-247",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1186,
            697,
            90,
            22
          ],
          "text": "prepend ph2"
        }
      },
      {
        "box": {
          "id": "obj-248",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ],
          "patching_rect": [
            1250,
            670,
            48,
            22
          ],
          "text": "abs 0."
        }
      },
      {
        "box": {
          "id": "obj-249",
          "maxclass": "newobj",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ],
          "patching_rect": [
            1250,
            697,
            48,
            22
          ],
          "text": "* 1.6"
        }
      },
      {
        "box": {
          "id": "obj-250",
          "maxclass": "newobj",
          "numinlets": 3,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1250,
            724,
            72,
            22
          ],
          "text": "clip 0. 1."
        }
      },
      {
        "box": {
          "id": "obj-251",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1250,
            751,
            82,
            22
          ],
          "text": "prepend m3"
        }
      },
      {
        "box": {
          "id": "obj-252",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1336,
            670,
            155,
            22
          ],
          "text": "expr ($f1 < 0.) * 3.141593"
        }
      },
      {
        "box": {
          "id": "obj-253",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1336,
            697,
            90,
            22
          ],
          "text": "prepend ph3"
        }
      },
      {
        "box": {
          "id": "obj-254",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ],
          "patching_rect": [
            1400,
            670,
            48,
            22
          ],
          "text": "abs 0."
        }
      },
      {
        "box": {
          "id": "obj-255",
          "maxclass": "newobj",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ],
          "patching_rect": [
            1400,
            697,
            48,
            22
          ],
          "text": "* 1.6"
        }
      },
      {
        "box": {
          "id": "obj-256",
          "maxclass": "newobj",
          "numinlets": 3,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1400,
            724,
            72,
            22
          ],
          "text": "clip 0. 1."
        }
      },
      {
        "box": {
          "id": "obj-257",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1400,
            751,
            82,
            22
          ],
          "text": "prepend m4"
        }
      },
      {
        "box": {
          "id": "obj-258",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1486,
            670,
            155,
            22
          ],
          "text": "expr ($f1 < 0.) * 3.141593"
        }
      },
      {
        "box": {
          "id": "obj-259",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1486,
            697,
            90,
            22
          ],
          "text": "prepend ph4"
        }
      },
      {
        "box": {
          "id": "obj-260",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ],
          "patching_rect": [
            800,
            800,
            48,
            22
          ],
          "text": "abs 0."
        }
      },
      {
        "box": {
          "id": "obj-261",
          "maxclass": "newobj",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ],
          "patching_rect": [
            800,
            827,
            48,
            22
          ],
          "text": "* 1.6"
        }
      },
      {
        "box": {
          "id": "obj-262",
          "maxclass": "newobj",
          "numinlets": 3,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            800,
            854,
            72,
            22
          ],
          "text": "clip 0. 1."
        }
      },
      {
        "box": {
          "id": "obj-263",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            800,
            881,
            82,
            22
          ],
          "text": "prepend m5"
        }
      },
      {
        "box": {
          "id": "obj-264",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            886,
            800,
            155,
            22
          ],
          "text": "expr ($f1 < 0.) * 3.141593"
        }
      },
      {
        "box": {
          "id": "obj-265",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            886,
            827,
            90,
            22
          ],
          "text": "prepend ph5"
        }
      },
      {
        "box": {
          "id": "obj-266",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ],
          "patching_rect": [
            950,
            800,
            48,
            22
          ],
          "text": "abs 0."
        }
      },
      {
        "box": {
          "id": "obj-267",
          "maxclass": "newobj",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ],
          "patching_rect": [
            950,
            827,
            48,
            22
          ],
          "text": "* 1.6"
        }
      },
      {
        "box": {
          "id": "obj-268",
          "maxclass": "newobj",
          "numinlets": 3,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            950,
            854,
            72,
            22
          ],
          "text": "clip 0. 1."
        }
      },
      {
        "box": {
          "id": "obj-269",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            950,
            881,
            82,
            22
          ],
          "text": "prepend m6"
        }
      },
      {
        "box": {
          "id": "obj-270",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1036,
            800,
            155,
            22
          ],
          "text": "expr ($f1 < 0.) * 3.141593"
        }
      },
      {
        "box": {
          "id": "obj-271",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1036,
            827,
            90,
            22
          ],
          "text": "prepend ph6"
        }
      },
      {
        "box": {
          "id": "obj-272",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ],
          "patching_rect": [
            1100,
            800,
            48,
            22
          ],
          "text": "abs 0."
        }
      },
      {
        "box": {
          "id": "obj-273",
          "maxclass": "newobj",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ],
          "patching_rect": [
            1100,
            827,
            48,
            22
          ],
          "text": "* 1.6"
        }
      },
      {
        "box": {
          "id": "obj-274",
          "maxclass": "newobj",
          "numinlets": 3,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1100,
            854,
            72,
            22
          ],
          "text": "clip 0. 1."
        }
      },
      {
        "box": {
          "id": "obj-275",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1100,
            881,
            82,
            22
          ],
          "text": "prepend m7"
        }
      },
      {
        "box": {
          "id": "obj-276",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1186,
            800,
            155,
            22
          ],
          "text": "expr ($f1 < 0.) * 3.141593"
        }
      },
      {
        "box": {
          "id": "obj-277",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1186,
            827,
            90,
            22
          ],
          "text": "prepend ph7"
        }
      },
      {
        "box": {
          "id": "obj-278",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ],
          "patching_rect": [
            1250,
            800,
            48,
            22
          ],
          "text": "abs 0."
        }
      },
      {
        "box": {
          "id": "obj-279",
          "maxclass": "newobj",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ],
          "patching_rect": [
            1250,
            827,
            48,
            22
          ],
          "text": "* 1.6"
        }
      },
      {
        "box": {
          "id": "obj-280",
          "maxclass": "newobj",
          "numinlets": 3,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1250,
            854,
            72,
            22
          ],
          "text": "clip 0. 1."
        }
      },
      {
        "box": {
          "id": "obj-281",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1250,
            881,
            82,
            22
          ],
          "text": "prepend m8"
        }
      },
      {
        "box": {
          "id": "obj-282",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1336,
            800,
            155,
            22
          ],
          "text": "expr ($f1 < 0.) * 3.141593"
        }
      },
      {
        "box": {
          "id": "obj-283",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1336,
            827,
            90,
            22
          ],
          "text": "prepend ph8"
        }
      },
      {
        "box": {
          "id": "obj-284",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ],
          "patching_rect": [
            1400,
            800,
            48,
            22
          ],
          "text": "abs 0."
        }
      },
      {
        "box": {
          "id": "obj-285",
          "maxclass": "newobj",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ],
          "patching_rect": [
            1400,
            827,
            48,
            22
          ],
          "text": "* 1.6"
        }
      },
      {
        "box": {
          "id": "obj-286",
          "maxclass": "newobj",
          "numinlets": 3,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1400,
            854,
            72,
            22
          ],
          "text": "clip 0. 1."
        }
      },
      {
        "box": {
          "id": "obj-287",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1400,
            881,
            82,
            22
          ],
          "text": "prepend m9"
        }
      },
      {
        "box": {
          "id": "obj-288",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1486,
            800,
            155,
            22
          ],
          "text": "expr ($f1 < 0.) * 3.141593"
        }
      },
      {
        "box": {
          "id": "obj-289",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1486,
            827,
            90,
            22
          ],
          "text": "prepend ph9"
        }
      },
      {
        "box": {
          "id": "obj-290",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ],
          "patching_rect": [
            800,
            930,
            48,
            22
          ],
          "text": "abs 0."
        }
      },
      {
        "box": {
          "id": "obj-291",
          "maxclass": "newobj",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ],
          "patching_rect": [
            800,
            957,
            48,
            22
          ],
          "text": "* 1.6"
        }
      },
      {
        "box": {
          "id": "obj-292",
          "maxclass": "newobj",
          "numinlets": 3,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            800,
            984,
            72,
            22
          ],
          "text": "clip 0. 1."
        }
      },
      {
        "box": {
          "id": "obj-293",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            800,
            1011,
            82,
            22
          ],
          "text": "prepend m10"
        }
      },
      {
        "box": {
          "id": "obj-294",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            886,
            930,
            155,
            22
          ],
          "text": "expr ($f1 < 0.) * 3.141593"
        }
      },
      {
        "box": {
          "id": "obj-295",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            886,
            957,
            90,
            22
          ],
          "text": "prepend ph10"
        }
      },
      {
        "box": {
          "id": "obj-296",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ],
          "patching_rect": [
            950,
            930,
            48,
            22
          ],
          "text": "abs 0."
        }
      },
      {
        "box": {
          "id": "obj-297",
          "maxclass": "newobj",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ],
          "patching_rect": [
            950,
            957,
            48,
            22
          ],
          "text": "* 1.6"
        }
      },
      {
        "box": {
          "id": "obj-298",
          "maxclass": "newobj",
          "numinlets": 3,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            950,
            984,
            72,
            22
          ],
          "text": "clip 0. 1."
        }
      },
      {
        "box": {
          "id": "obj-299",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            950,
            1011,
            82,
            22
          ],
          "text": "prepend m11"
        }
      },
      {
        "box": {
          "id": "obj-300",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1036,
            930,
            155,
            22
          ],
          "text": "expr ($f1 < 0.) * 3.141593"
        }
      },
      {
        "box": {
          "id": "obj-301",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1036,
            957,
            90,
            22
          ],
          "text": "prepend ph11"
        }
      },
      {
        "box": {
          "id": "obj-302",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ],
          "patching_rect": [
            1100,
            930,
            48,
            22
          ],
          "text": "abs 0."
        }
      },
      {
        "box": {
          "id": "obj-303",
          "maxclass": "newobj",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ],
          "patching_rect": [
            1100,
            957,
            48,
            22
          ],
          "text": "* 1.6"
        }
      },
      {
        "box": {
          "id": "obj-304",
          "maxclass": "newobj",
          "numinlets": 3,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1100,
            984,
            72,
            22
          ],
          "text": "clip 0. 1."
        }
      },
      {
        "box": {
          "id": "obj-305",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1100,
            1011,
            82,
            22
          ],
          "text": "prepend m12"
        }
      },
      {
        "box": {
          "id": "obj-306",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1186,
            930,
            155,
            22
          ],
          "text": "expr ($f1 < 0.) * 3.141593"
        }
      },
      {
        "box": {
          "id": "obj-307",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1186,
            957,
            90,
            22
          ],
          "text": "prepend ph12"
        }
      },
      {
        "box": {
          "id": "obj-308",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ],
          "patching_rect": [
            1250,
            930,
            48,
            22
          ],
          "text": "abs 0."
        }
      },
      {
        "box": {
          "id": "obj-309",
          "maxclass": "newobj",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ],
          "patching_rect": [
            1250,
            957,
            48,
            22
          ],
          "text": "* 1.6"
        }
      },
      {
        "box": {
          "id": "obj-310",
          "maxclass": "newobj",
          "numinlets": 3,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1250,
            984,
            72,
            22
          ],
          "text": "clip 0. 1."
        }
      },
      {
        "box": {
          "id": "obj-311",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1250,
            1011,
            82,
            22
          ],
          "text": "prepend m13"
        }
      },
      {
        "box": {
          "id": "obj-312",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1336,
            930,
            155,
            22
          ],
          "text": "expr ($f1 < 0.) * 3.141593"
        }
      },
      {
        "box": {
          "id": "obj-313",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1336,
            957,
            90,
            22
          ],
          "text": "prepend ph13"
        }
      },
      {
        "box": {
          "id": "obj-314",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ],
          "patching_rect": [
            1400,
            930,
            48,
            22
          ],
          "text": "abs 0."
        }
      },
      {
        "box": {
          "id": "obj-315",
          "maxclass": "newobj",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ],
          "patching_rect": [
            1400,
            957,
            48,
            22
          ],
          "text": "* 1.6"
        }
      },
      {
        "box": {
          "id": "obj-316",
          "maxclass": "newobj",
          "numinlets": 3,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1400,
            984,
            72,
            22
          ],
          "text": "clip 0. 1."
        }
      },
      {
        "box": {
          "id": "obj-317",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1400,
            1011,
            82,
            22
          ],
          "text": "prepend m14"
        }
      },
      {
        "box": {
          "id": "obj-318",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1486,
            930,
            155,
            22
          ],
          "text": "expr ($f1 < 0.) * 3.141593"
        }
      },
      {
        "box": {
          "id": "obj-319",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1486,
            957,
            90,
            22
          ],
          "text": "prepend ph14"
        }
      },
      {
        "box": {
          "id": "obj-320",
          "maxclass": "message",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            800,
            1065,
            135,
            22
          ],
          "text": "m15 0, ph15 0"
        }
      },
      {
        "box": {
          "id": "obj-321",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            1030,
            385,
            120,
            20
          ],
          "presentation": 1,
          "presentation_rect": [
            1030,
            375,
            120,
            20
          ],
          "text": "Master level (dB)"
        }
      },
      {
        "box": {
          "format": 6,
          "id": "obj-322",
          "maxclass": "flonum",
          "maximum": 0,
          "minimum": -60,
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "",
            "bang"
          ],
          "parameter_enable": 0,
          "patching_rect": [
            1150,
            380,
            75,
            22
          ],
          "presentation": 1,
          "presentation_rect": [
            1150,
            370,
            75,
            22
          ]
        }
      },
      {
        "box": {
          "id": "obj-323",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1235,
            380,
            90,
            22
          ],
          "text": "loadmess -10."
        }
      },
      {
        "box": {
          "id": "obj-324",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1150,
            410,
            48,
            22
          ],
          "text": "dbtoa"
        }
      },
      {
        "box": {
          "id": "obj-325",
          "maxclass": "newobj",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1205,
            410,
            78,
            22
          ],
          "text": "pack 0. 60"
        }
      },
      {
        "box": {
          "id": "obj-326",
          "maxclass": "newobj",
          "numinlets": 2,
          "numoutlets": 2,
          "outlettype": [
            "signal",
            "bang"
          ],
          "patching_rect": [
            1290,
            410,
            48,
            22
          ],
          "text": "line~"
        }
      },
      {
        "box": {
          "id": "obj-327",
          "maxclass": "newobj",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ],
          "patching_rect": [
            1210,
            900,
            40,
            22
          ],
          "text": "*~"
        }
      },
      {
        "box": {
          "id": "obj-328",
          "maxclass": "newobj",
          "numinlets": 3,
          "numoutlets": 1,
          "outlettype": [
            "signal"
          ],
          "patching_rect": [
            1260,
            900,
            95,
            22
          ],
          "text": "clip~ -0.9 0.9"
        }
      },
      {
        "box": {
          "id": "obj-329",
          "maxclass": "meter~",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "float"
          ],
          "patching_rect": [
            1030,
            455,
            195,
            16
          ],
          "presentation": 1,
          "presentation_rect": [
            1030,
            420,
            195,
            16
          ]
        }
      },
      {
        "box": {
          "id": "obj-330",
          "local": 1,
          "maxclass": "ezdac~",
          "numinlets": 2,
          "numoutlets": 0,
          "patching_rect": [
            1157,
            1039,
            48,
            48
          ],
          "presentation": 1,
          "presentation_rect": [
            1260,
            405,
            48,
            48
          ]
        }
      },
      {
        "box": {
          "id": "obj-400",
          "maxclass": "newobj",
          "patching_rect": [
            20,
            850,
            115,
            22
          ],
          "text": "udpreceive 7400"
        }
      },
      {
        "box": {
          "id": "obj-401",
          "maxclass": "newobj",
          "patching_rect": [
            145,
            850,
            105,
            22
          ],
          "text": "OSC-route /qmw"
        }
      },
      {
        "box": {
          "id": "obj-402",
          "maxclass": "newobj",
          "patching_rect": [
            260,
            850,
            110,
            22
          ],
          "text": "OSC-route /bloch"
        }
      },
      {
        "box": {
          "id": "obj-403",
          "maxclass": "newobj",
          "patching_rect": [
            380,
            850,
            245,
            22
          ],
          "text": "OSC-route /vector_x /vector_y /vector_z"
        }
      },
      {
        "box": {
          "id": "obj-404",
          "maxclass": "newobj",
          "patching_rect": [
            635,
            850,
            70,
            22
          ],
          "text": "pak f f f"
        }
      },
      {
        "box": {
          "id": "obj-405",
          "maxclass": "newobj",
          "patching_rect": [
            715,
            835,
            430,
            22
          ],
          "text": "expr acos(max(-1., min(1., $f3 / max(sqrt($f1*$f1+$f2*$f2+$f3*$f3), 0.000001))))"
        }
      },
      {
        "box": {
          "id": "obj-406",
          "maxclass": "newobj",
          "patching_rect": [
            715,
            865,
            128,
            22
          ],
          "text": "expr atan2($f2, $f1)"
        }
      },
      {
        "box": {
          "id": "obj-407",
          "maxclass": "newobj",
          "patching_rect": [
            1155,
            835,
            92,
            22
          ],
          "text": "* 57.2957795"
        }
      },
      {
        "box": {
          "id": "obj-408",
          "maxclass": "newobj",
          "patching_rect": [
            1155,
            865,
            92,
            22
          ],
          "text": "* 57.2957795"
        }
      },
      {
        "box": {
          "id": "obj-409",
          "maxclass": "newobj",
          "patching_rect": [
            1257,
            850,
            58,
            22
          ],
          "text": "pak f f"
        }
      },
      {
        "box": {
          "id": "obj-410",
          "maxclass": "newobj",
          "patching_rect": [
            1325,
            850,
            48,
            22
          ],
          "text": "gate 1"
        }
      },
      {
        "box": {
          "id": "obj-411",
          "maxclass": "newobj",
          "patching_rect": [
            1383,
            850,
            118,
            22
          ],
          "text": "prepend setAngles"
        }
      },
      {
        "box": {
          "id": "obj-412",
          "maxclass": "toggle",
          "patching_rect": [
            1030,
            500,
            24,
            24
          ],
          "presentation": 1,
          "presentation_rect": [
            1030,
            475,
            24,
            24
          ]
        }
      },
      {
        "box": {
          "id": "obj-413",
          "maxclass": "comment",
          "patching_rect": [
            1060,
            502,
            130,
            20
          ],
          "text": "OSC angle drive",
          "presentation": 1,
          "presentation_rect": [
            1060,
            477,
            130,
            20
          ]
        }
      },
      {
        "box": {
          "id": "obj-414",
          "maxclass": "newobj",
          "patching_rect": [
            1195,
            500,
            82,
            22
          ],
          "text": "loadmess 1"
        }
      },
      {
        "box": {
          "id": "obj-415",
          "maxclass": "button",
          "patching_rect": [
            1030,
            535,
            24,
            24
          ],
          "presentation": 1,
          "presentation_rect": [
            1030,
            510,
            24,
            24
          ]
        }
      },
      {
        "box": {
          "id": "obj-416",
          "maxclass": "comment",
          "patching_rect": [
            1060,
            537,
            210,
            20
          ],
          "text": "density OSC activity · UDP 7400",
          "presentation": 1,
          "presentation_rect": [
            1060,
            512,
            230,
            20
          ]
        }
      },
      {
        "box": {
          "id": "obj-417",
          "maxclass": "comment",
          "patching_rect": [
            1030,
            572,
            90,
            20
          ],
          "text": "OSC θ (°)",
          "presentation": 1,
          "presentation_rect": [
            1030,
            547,
            90,
            20
          ]
        }
      },
      {
        "box": {
          "id": "obj-418",
          "maxclass": "flonum",
          "patching_rect": [
            1120,
            567,
            90,
            24
          ],
          "presentation": 1,
          "presentation_rect": [
            1120,
            542,
            90,
            24
          ]
        }
      },
      {
        "box": {
          "id": "obj-419",
          "maxclass": "comment",
          "patching_rect": [
            1030,
            607,
            90,
            20
          ],
          "text": "OSC φ (°)",
          "presentation": 1,
          "presentation_rect": [
            1030,
            582,
            90,
            20
          ]
        }
      },
      {
        "box": {
          "id": "obj-420",
          "maxclass": "flonum",
          "patching_rect": [
            1120,
            602,
            90,
            24
          ],
          "presentation": 1,
          "presentation_rect": [
            1120,
            577,
            90,
            24
          ]
        }
      },
      {
        "box": {
          "id": "obj-421",
          "maxclass": "comment",
          "patching_rect": [
            1030,
            642,
            330,
            40
          ],
          "linecount": 2,
          "text": "Source: /qmw/bloch/vector_x, vector_y, vector_z\\nθ = acos(z/r),  φ = atan2(y,x)",
          "presentation": 1,
          "presentation_rect": [
            1030,
            617,
            330,
            40
          ]
        }
      },
      {
        "box": {
          "id": "obj-500",
          "maxclass": "newobj",
          "patching_rect": [
            850,
            1120,
            210,
            22
          ],
          "text": "qmw_bloch_convolution_ir~"
        }
      },
      {
        "box": {
          "id": "obj-501",
          "maxclass": "comment",
          "patching_rect": [
            1030,
            690,
            260,
            22
          ],
          "fontsize": 14,
          "text": "Dual-geometry convolution IR",
          "presentation": 1,
          "presentation_rect": [
            1030,
            665,
            280,
            22
          ]
        }
      },
      {
        "box": {
          "id": "obj-502",
          "maxclass": "comment",
          "patching_rect": [
            1030,
            725,
            110,
            20
          ],
          "text": "Convolution mix",
          "presentation": 1,
          "presentation_rect": [
            1030,
            700,
            110,
            20
          ]
        }
      },
      {
        "box": {
          "id": "obj-503",
          "maxclass": "flonum",
          "patching_rect": [
            1150,
            720,
            80,
            24
          ],
          "minimum": 0,
          "maximum": 1,
          "presentation": 1,
          "presentation_rect": [
            1150,
            695,
            80,
            24
          ]
        }
      },
      {
        "box": {
          "id": "obj-504",
          "maxclass": "newobj",
          "patching_rect": [
            1240,
            720,
            95,
            22
          ],
          "text": "loadmess 0.35"
        }
      },
      {
        "box": {
          "id": "obj-505",
          "maxclass": "newobj",
          "patching_rect": [
            1150,
            755,
            42,
            22
          ],
          "text": "t f f"
        }
      },
      {
        "box": {
          "id": "obj-506",
          "maxclass": "newobj",
          "patching_rect": [
            1200,
            755,
            92,
            22
          ],
          "text": "expr sqrt($f1)"
        }
      },
      {
        "box": {
          "id": "obj-507",
          "maxclass": "newobj",
          "patching_rect": [
            1090,
            755,
            43,
            22
          ],
          "text": "expr sqrt(max(0., 1. - $f1))"
        }
      },
      {
        "box": {
          "id": "obj-508",
          "maxclass": "newobj",
          "patching_rect": [
            1020,
            785,
            92,
            22
          ],
          "text": "expr sqrt($f1)"
        }
      },
      {
        "box": {
          "id": "obj-509",
          "maxclass": "newobj",
          "patching_rect": [
            1120,
            785,
            35,
            22
          ],
          "text": "sig~"
        }
      },
      {
        "box": {
          "id": "obj-510",
          "maxclass": "newobj",
          "patching_rect": [
            1165,
            1120,
            35,
            22
          ],
          "text": "*~"
        }
      },
      {
        "box": {
          "id": "obj-511",
          "maxclass": "newobj",
          "patching_rect": [
            1070,
            1155,
            35,
            22
          ],
          "text": "+~"
        }
      },
      {
        "box": {
          "id": "obj-512",
          "maxclass": "newobj",
          "patching_rect": [
            1160,
            1155,
            35,
            22
          ],
          "text": "+~"
        }
      },
      {
        "box": {
          "id": "obj-513",
          "maxclass": "newobj",
          "patching_rect": [
            1000,
            1120,
            58,
            22
          ],
          "text": "dcblocker~"
        }
      },
      {
        "box": {
          "id": "obj-514",
          "maxclass": "newobj",
          "patching_rect": [
            1070,
            1120,
            58,
            22
          ],
          "text": "dcblocker~"
        }
      },
      {
        "box": {
          "id": "obj-515",
          "maxclass": "newobj",
          "patching_rect": [
            1070,
            1190,
            95,
            22
          ],
          "text": "clip~ -0.9 0.9"
        }
      },
      {
        "box": {
          "id": "obj-516",
          "maxclass": "newobj",
          "patching_rect": [
            1175,
            1190,
            95,
            22
          ],
          "text": "clip~ -0.9 0.9"
        }
      },
      {
        "box": {
          "id": "obj-517",
          "maxclass": "comment",
          "patching_rect": [
            1030,
            760,
            110,
            20
          ],
          "text": "IR geometry",
          "presentation": 1,
          "presentation_rect": [
            1030,
            735,
            110,
            20
          ]
        }
      },
      {
        "box": {
          "id": "obj-518",
          "maxclass": "flonum",
          "patching_rect": [
            1150,
            755,
            80,
            24
          ],
          "minimum": 0,
          "maximum": 1,
          "presentation": 1,
          "presentation_rect": [
            1150,
            730,
            80,
            24
          ]
        }
      },
      {
        "box": {
          "id": "obj-519",
          "maxclass": "newobj",
          "patching_rect": [
            1240,
            755,
            82,
            22
          ],
          "text": "loadmess 0."
        }
      },
      {
        "box": {
          "id": "obj-520",
          "maxclass": "comment",
          "patching_rect": [
            1030,
            790,
            300,
            20
          ],
          "text": "0 = Tanglecube  ·  1 = Heart",
          "presentation": 1,
          "presentation_rect": [
            1030,
            765,
            300,
            20
          ]
        }
      },
      {
        "box": {
          "id": "obj-521",
          "maxclass": "comment",
          "patching_rect": [
            1360,
            720,
            36,
            20
          ],
          "text": "IR A",
          "presentation": 1,
          "presentation_rect": [
            1240,
            700,
            36,
            20
          ]
        }
      },
      {
        "box": {
          "id": "obj-522",
          "maxclass": "message",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1400,
            720,
            62,
            22
          ],
          "text": "replace",
          "presentation": 1,
          "presentation_rect": [
            1278,
            698,
            62,
            22
          ]
        }
      },
      {
        "box": {
          "id": "obj-523",
          "maxclass": "comment",
          "patching_rect": [
            1360,
            755,
            36,
            20
          ],
          "text": "IR B",
          "presentation": 1,
          "presentation_rect": [
            1240,
            735,
            36,
            20
          ]
        }
      },
      {
        "box": {
          "id": "obj-524",
          "maxclass": "message",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            1400,
            755,
            62,
            22
          ],
          "text": "replace",
          "presentation": 1,
          "presentation_rect": [
            1278,
            733,
            62,
            22
          ]
        }
      },
      {
        "box": {
          "id": "obj-530",
          "maxclass": "newobj",
          "patching_rect": [20, 1080, 125, 22],
          "text": "OSC-route /density"
        }
      },
      {
        "box": {
          "id": "obj-531",
          "maxclass": "newobj",
          "patching_rect": [155, 1080, 350, 22],
          "text": "OSC-route /coherence_l1 /von_neumann_entropy /purity"
        }
      },
      {
        "box": {
          "id": "obj-532",
          "maxclass": "newobj",
          "patching_rect": [155, 1110, 45, 22],
          "text": "/ 15."
        }
      },
      {
        "box": {
          "id": "obj-533",
          "maxclass": "newobj",
          "patching_rect": [210, 1110, 68, 22],
          "text": "clip 0. 1."
        }
      },
      {
        "box": {
          "id": "obj-534",
          "maxclass": "newobj",
          "patching_rect": [288, 1110, 78, 22],
          "text": "pack 0. 180"
        }
      },
      {
        "box": {
          "id": "obj-535",
          "maxclass": "newobj",
          "patching_rect": [376, 1110, 48, 22],
          "text": "line 0."
        }
      },
      {
        "box": {
          "id": "obj-536",
          "maxclass": "newobj",
          "patching_rect": [434, 1110, 42, 22],
          "text": "t f f"
        }
      },
      {
        "box": {
          "id": "obj-537",
          "maxclass": "newobj",
          "patching_rect": [486, 1110, 125, 22],
          "text": "prepend coherence"
        }
      },
      {
        "box": {
          "id": "obj-538",
          "maxclass": "newobj",
          "patching_rect": [155, 1140, 92, 22],
          "text": "/ 2.772588722"
        }
      },
      {
        "box": {
          "id": "obj-539",
          "maxclass": "newobj",
          "patching_rect": [257, 1140, 68, 22],
          "text": "clip 0. 1."
        }
      },
      {
        "box": {
          "id": "obj-540",
          "maxclass": "newobj",
          "patching_rect": [335, 1140, 78, 22],
          "text": "pack 0. 180"
        }
      },
      {
        "box": {
          "id": "obj-541",
          "maxclass": "newobj",
          "patching_rect": [423, 1140, 48, 22],
          "text": "line 0."
        }
      },
      {
        "box": {
          "id": "obj-542",
          "maxclass": "newobj",
          "patching_rect": [481, 1140, 110, 22],
          "text": "prepend entropy"
        }
      },
      {
        "box": {
          "id": "obj-543",
          "maxclass": "newobj",
          "patching_rect": [515, 1080, 68, 22],
          "text": "clip 0. 1."
        }
      },
      {
        "box": {
          "id": "obj-544",
          "maxclass": "newobj",
          "patching_rect": [593, 1080, 78, 22],
          "text": "pack 0. 180"
        }
      },
      {
        "box": {
          "id": "obj-545",
          "maxclass": "newobj",
          "patching_rect": [681, 1080, 48, 22],
          "text": "line 0."
        }
      },
      {
        "box": {
          "id": "obj-546",
          "maxclass": "newobj",
          "patching_rect": [434, 1170, 60, 22],
          "text": "pak f f"
        }
      },
      {
        "box": {
          "id": "obj-547",
          "maxclass": "newobj",
          "patching_rect": [504, 1170, 270, 22],
          "text": "expr max(0.05,min(1.,0.9-0.75*$f1+$f2))"
        }
      },
      {
        "box": {
          "id": "obj-548",
          "maxclass": "comment",
          "patching_rect": [1000, 415, 230, 20],
          "text": "OSC coherence + entropy; manual offset",
          "presentation": 1,
          "presentation_rect": [1000, 400, 230, 20]
        }
      },
      {
        "box": {
          "id": "obj-600",
          "maxclass": "newobj",
          "patching_rect": [850, 1260, 205, 22],
          "text": "qmw_bloch_spat5~"
        }
      },
      {
        "box": {
          "id": "obj-601",
          "maxclass": "comment",
          "patching_rect": [790, 1230, 240, 22],
          "text": "SPAT5 BLOCH AED",
          "presentation": 1,
          "presentation_rect": [790, 810, 240, 22]
        }
      },
      {
        "box": {
          "id": "obj-602",
          "maxclass": "comment",
          "patching_rect": [790, 1260, 105, 20],
          "text": "Spatial amount",
          "presentation": 1,
          "presentation_rect": [790, 845, 105, 20]
        }
      },
      {
        "box": {
          "format": 6,
          "id": "obj-603",
          "maxclass": "flonum",
          "minimum": 0,
          "maximum": 1,
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": ["", "bang"],
          "patching_rect": [900, 1255, 80, 24],
          "presentation": 1,
          "presentation_rect": [900, 840, 80, 24]
        }
      },
      {
        "box": {
          "id": "obj-604",
          "maxclass": "newobj",
          "patching_rect": [990, 1255, 82, 22],
          "text": "loadmess 1."
        }
      },
      {
        "box": {
          "id": "obj-605",
          "maxclass": "comment",
          "linecount": 2,
          "patching_rect": [1030, 1230, 360, 40],
          "text": "Bloch φ / elevation / radius → AED\nPurity → aperture  ·  Bohmian local phase → yaw",
          "presentation": 1,
          "presentation_rect": [1030, 805, 360, 40]
        }
      },
      {
        "box": {
          "id": "obj-606",
          "maxclass": "comment",
          "patching_rect": [1030, 1295, 35, 20],
          "text": "Az°",
          "presentation": 1,
          "presentation_rect": [1030, 850, 35, 20]
        }
      },
      {
        "box": {
          "format": 6,
          "id": "obj-607",
          "ignoreclick": 1,
          "maxclass": "flonum",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": ["", "bang"],
          "patching_rect": [1068, 1290, 75, 24],
          "presentation": 1,
          "presentation_rect": [1068, 845, 75, 24]
        }
      },
      {
        "box": {
          "id": "obj-608",
          "maxclass": "comment",
          "patching_rect": [1150, 1295, 30, 20],
          "text": "El°",
          "presentation": 1,
          "presentation_rect": [1150, 850, 30, 20]
        }
      },
      {
        "box": {
          "format": 6,
          "id": "obj-609",
          "ignoreclick": 1,
          "maxclass": "flonum",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": ["", "bang"],
          "patching_rect": [1182, 1290, 75, 24],
          "presentation": 1,
          "presentation_rect": [1182, 845, 75, 24]
        }
      },
      {
        "box": {
          "id": "obj-610",
          "maxclass": "comment",
          "patching_rect": [1265, 1295, 38, 20],
          "text": "Dist",
          "presentation": 1,
          "presentation_rect": [1265, 850, 38, 20]
        }
      },
      {
        "box": {
          "format": 6,
          "id": "obj-611",
          "ignoreclick": 1,
          "maxclass": "flonum",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": ["", "bang"],
          "patching_rect": [1305, 1290, 75, 24],
          "presentation": 1,
          "presentation_rect": [1305, 845, 75, 24]
        }
      },
      {
        "box": {
          "id": "obj-612",
          "maxclass": "newobj",
          "patching_rect": [1070, 1340, 95, 22],
          "text": "clip~ -0.9 0.9"
        }
      },
      {
        "box": {
          "id": "obj-613",
          "maxclass": "newobj",
          "patching_rect": [1175, 1340, 95, 22],
          "text": "clip~ -0.9 0.9"
        }
      },
      {
        "box": {
          "id": "obj-614",
          "maxclass": "comment",
          "patching_rect": [1030, 1380, 62, 20],
          "text": "Aperture out°",
          "presentation": 1,
          "presentation_rect": [1030, 885, 90, 20]
        }
      },
      {
        "box": {
          "format": 6,
          "id": "obj-615",
          "ignoreclick": 1,
          "maxclass": "flonum",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": ["", "bang"],
          "patching_rect": [1120, 1375, 75, 24],
          "presentation": 1,
          "presentation_rect": [1120, 880, 75, 24]
        }
      },
      {
        "box": {
          "id": "obj-616",
          "maxclass": "comment",
          "patching_rect": [1190, 1380, 38, 20],
          "text": "Yaw out°",
          "presentation": 1,
          "presentation_rect": [1210, 885, 60, 20]
        }
      },
      {
        "box": {
          "format": 6,
          "id": "obj-617",
          "ignoreclick": 1,
          "maxclass": "flonum",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": ["", "bang"],
          "patching_rect": [1272, 1375, 75, 24],
          "presentation": 1,
          "presentation_rect": [1272, 880, 75, 24]
        }
      },
      {
        "box": {
          "id": "obj-620",
          "maxclass": "newobj",
          "patching_rect": [20, 1210, 112, 22],
          "text": "OSC-route /bohm"
        }
      },
      {
        "box": {
          "id": "obj-621",
          "maxclass": "newobj",
          "patching_rect": [142, 1210, 110, 22],
          "text": "OSC-route /phase"
        }
      },
      {
        "box": {
          "id": "obj-622",
          "maxclass": "newobj",
          "patching_rect": [262, 1210, 78, 22],
          "text": "pack 0. 180"
        }
      },
      {
        "box": {
          "id": "obj-623",
          "maxclass": "newobj",
          "patching_rect": [350, 1210, 48, 22],
          "text": "line 0."
        }
      },
      {
        "box": {
          "id": "obj-618",
          "maxclass": "comment",
          "patching_rect": [790, 1410, 105, 20],
          "text": "Aperture trim°",
          "presentation": 1,
          "presentation_rect": [790, 885, 105, 20]
        }
      },
      {
        "box": {
          "format": 6,
          "id": "obj-619",
          "maxclass": "flonum",
          "minimum": -160,
          "maximum": 160,
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": ["", "bang"],
          "patching_rect": [900, 1405, 80, 24],
          "presentation": 1,
          "presentation_rect": [900, 880, 80, 24]
        }
      },
      {
        "box": {
          "id": "obj-624",
          "maxclass": "newobj",
          "patching_rect": [990, 1405, 82, 22],
          "text": "loadmess 0."
        }
      },
      {
        "box": {
          "id": "obj-625",
          "maxclass": "comment",
          "patching_rect": [790, 1440, 105, 20],
          "text": "Yaw trim°",
          "presentation": 1,
          "presentation_rect": [790, 915, 105, 20]
        }
      },
      {
        "box": {
          "format": 6,
          "id": "obj-626",
          "maxclass": "flonum",
          "minimum": -180,
          "maximum": 180,
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": ["", "bang"],
          "patching_rect": [900, 1435, 80, 24],
          "presentation": 1,
          "presentation_rect": [900, 910, 80, 24]
        }
      },
      {
        "box": {
          "id": "obj-627",
          "maxclass": "newobj",
          "patching_rect": [990, 1435, 82, 22],
          "text": "loadmess 0."
        }
      }
    ],
    "lines": [
      {
        "patchline": {
          "destination": [
            "obj-124",
            0
          ],
          "order": 0,
          "source": [
            "obj-123",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-8",
            0
          ],
          "order": 1,
          "source": [
            "obj-123",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-327",
            0
          ],
          "hidden": 1,
          "source": [
            "obj-200",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-204",
            0
          ],
          "source": [
            "obj-202",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-202",
            0
          ],
          "source": [
            "obj-203",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-200",
            0
          ],
          "hidden": 1,
          "source": [
            "obj-204",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-200",
            0
          ],
          "hidden": 1,
          "source": [
            "obj-207",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-206",
            0
          ],
          "source": [
            "obj-208",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-211",
            0
          ],
          "source": [
            "obj-210",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-200",
            0
          ],
          "hidden": 1,
          "source": [
            "obj-211",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-210",
            0
          ],
          "source": [
            "obj-212",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-215",
            0
          ],
          "source": [
            "obj-214",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-200",
            0
          ],
          "hidden": 1,
          "source": [
            "obj-215",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-214",
            0
          ],
          "source": [
            "obj-216",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-219",
            0
          ],
          "source": [
            "obj-218",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-200",
            0
          ],
          "hidden": 1,
          "source": [
            "obj-219",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-218",
            0
          ],
          "source": [
            "obj-220",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-223",
            0
          ],
          "source": [
            "obj-222",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-200",
            0
          ],
          "hidden": 1,
          "source": [
            "obj-223",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-222",
            0
          ],
          "source": [
            "obj-224",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-227",
            0
          ],
          "source": [
            "obj-226",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-200",
            0
          ],
          "hidden": 1,
          "source": [
            "obj-227",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-226",
            0
          ],
          "source": [
            "obj-228",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-200",
            0
          ],
          "hidden": 1,
          "source": [
            "obj-229",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-231",
            0
          ],
          "source": [
            "obj-230",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-232",
            0
          ],
          "source": [
            "obj-231",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-233",
            0
          ],
          "source": [
            "obj-232",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-200",
            0
          ],
          "hidden": 1,
          "source": [
            "obj-233",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-235",
            0
          ],
          "source": [
            "obj-234",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-200",
            0
          ],
          "hidden": 1,
          "source": [
            "obj-235",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-237",
            0
          ],
          "source": [
            "obj-236",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-238",
            0
          ],
          "source": [
            "obj-237",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-239",
            0
          ],
          "source": [
            "obj-238",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-200",
            0
          ],
          "hidden": 1,
          "source": [
            "obj-239",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-241",
            0
          ],
          "source": [
            "obj-240",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-200",
            0
          ],
          "hidden": 1,
          "source": [
            "obj-241",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-243",
            0
          ],
          "source": [
            "obj-242",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-244",
            0
          ],
          "source": [
            "obj-243",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-245",
            0
          ],
          "source": [
            "obj-244",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-200",
            0
          ],
          "hidden": 1,
          "source": [
            "obj-245",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-247",
            0
          ],
          "source": [
            "obj-246",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-200",
            0
          ],
          "hidden": 1,
          "source": [
            "obj-247",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-249",
            0
          ],
          "source": [
            "obj-248",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-250",
            0
          ],
          "source": [
            "obj-249",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-251",
            0
          ],
          "source": [
            "obj-250",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-200",
            0
          ],
          "hidden": 1,
          "source": [
            "obj-251",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-253",
            0
          ],
          "source": [
            "obj-252",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-200",
            0
          ],
          "hidden": 1,
          "source": [
            "obj-253",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-255",
            0
          ],
          "source": [
            "obj-254",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-256",
            0
          ],
          "source": [
            "obj-255",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-257",
            0
          ],
          "source": [
            "obj-256",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-200",
            0
          ],
          "hidden": 1,
          "source": [
            "obj-257",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-259",
            0
          ],
          "source": [
            "obj-258",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-200",
            0
          ],
          "hidden": 1,
          "source": [
            "obj-259",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-261",
            0
          ],
          "source": [
            "obj-260",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-262",
            0
          ],
          "source": [
            "obj-261",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-263",
            0
          ],
          "source": [
            "obj-262",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-200",
            0
          ],
          "hidden": 1,
          "source": [
            "obj-263",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-265",
            0
          ],
          "source": [
            "obj-264",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-200",
            0
          ],
          "hidden": 1,
          "source": [
            "obj-265",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-267",
            0
          ],
          "source": [
            "obj-266",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-268",
            0
          ],
          "source": [
            "obj-267",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-269",
            0
          ],
          "source": [
            "obj-268",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-200",
            0
          ],
          "hidden": 1,
          "source": [
            "obj-269",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-271",
            0
          ],
          "source": [
            "obj-270",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-200",
            0
          ],
          "hidden": 1,
          "source": [
            "obj-271",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-273",
            0
          ],
          "source": [
            "obj-272",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-274",
            0
          ],
          "source": [
            "obj-273",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-275",
            0
          ],
          "source": [
            "obj-274",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-200",
            0
          ],
          "hidden": 1,
          "source": [
            "obj-275",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-277",
            0
          ],
          "source": [
            "obj-276",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-200",
            0
          ],
          "hidden": 1,
          "source": [
            "obj-277",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-279",
            0
          ],
          "source": [
            "obj-278",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-280",
            0
          ],
          "source": [
            "obj-279",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-281",
            0
          ],
          "source": [
            "obj-280",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-200",
            0
          ],
          "hidden": 1,
          "source": [
            "obj-281",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-283",
            0
          ],
          "source": [
            "obj-282",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-200",
            0
          ],
          "hidden": 1,
          "source": [
            "obj-283",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-285",
            0
          ],
          "source": [
            "obj-284",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-286",
            0
          ],
          "source": [
            "obj-285",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-287",
            0
          ],
          "source": [
            "obj-286",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-200",
            0
          ],
          "hidden": 1,
          "source": [
            "obj-287",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-289",
            0
          ],
          "source": [
            "obj-288",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-200",
            0
          ],
          "hidden": 1,
          "source": [
            "obj-289",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-291",
            0
          ],
          "source": [
            "obj-290",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-292",
            0
          ],
          "source": [
            "obj-291",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-293",
            0
          ],
          "source": [
            "obj-292",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-200",
            0
          ],
          "hidden": 1,
          "source": [
            "obj-293",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-295",
            0
          ],
          "source": [
            "obj-294",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-200",
            0
          ],
          "hidden": 1,
          "source": [
            "obj-295",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-297",
            0
          ],
          "source": [
            "obj-296",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-298",
            0
          ],
          "source": [
            "obj-297",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-299",
            0
          ],
          "source": [
            "obj-298",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-200",
            0
          ],
          "hidden": 1,
          "source": [
            "obj-299",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-123",
            0
          ],
          "order": 0,
          "source": [
            "obj-3",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-6",
            0
          ],
          "order": 1,
          "source": [
            "obj-3",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-301",
            0
          ],
          "source": [
            "obj-300",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-200",
            0
          ],
          "hidden": 1,
          "source": [
            "obj-301",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-303",
            0
          ],
          "source": [
            "obj-302",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-304",
            0
          ],
          "source": [
            "obj-303",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-305",
            0
          ],
          "source": [
            "obj-304",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-200",
            0
          ],
          "hidden": 1,
          "source": [
            "obj-305",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-307",
            0
          ],
          "source": [
            "obj-306",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-200",
            0
          ],
          "hidden": 1,
          "source": [
            "obj-307",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-309",
            0
          ],
          "source": [
            "obj-308",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-310",
            0
          ],
          "source": [
            "obj-309",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-311",
            0
          ],
          "source": [
            "obj-310",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-200",
            0
          ],
          "hidden": 1,
          "source": [
            "obj-311",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-313",
            0
          ],
          "source": [
            "obj-312",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-200",
            0
          ],
          "hidden": 1,
          "source": [
            "obj-313",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-315",
            0
          ],
          "source": [
            "obj-314",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-316",
            0
          ],
          "source": [
            "obj-315",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-317",
            0
          ],
          "source": [
            "obj-316",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-200",
            0
          ],
          "hidden": 1,
          "source": [
            "obj-317",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-319",
            0
          ],
          "source": [
            "obj-318",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-200",
            0
          ],
          "hidden": 1,
          "source": [
            "obj-319",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-200",
            0
          ],
          "hidden": 1,
          "source": [
            "obj-320",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-324",
            0
          ],
          "source": [
            "obj-322",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-322",
            0
          ],
          "source": [
            "obj-323",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-325",
            0
          ],
          "source": [
            "obj-324",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-326",
            0
          ],
          "source": [
            "obj-325",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-327",
            1
          ],
          "source": [
            "obj-326",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-328",
            0
          ],
          "source": [
            "obj-327",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-229",
            0
          ],
          "order": 1,
          "source": [
            "obj-4",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-320",
            0
          ],
          "order": 0,
          "source": [
            "obj-4",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-5",
            0
          ],
          "order": 2,
          "source": [
            "obj-4",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-3",
            0
          ],
          "source": [
            "obj-5",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-7",
            0
          ],
          "source": [
            "obj-6",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-124",
            0
          ],
          "order": 0,
          "source": [
            "obj-7",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-8",
            0
          ],
          "order": 1,
          "source": [
            "obj-7",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-10",
            0
          ],
          "source": [
            "obj-8",
            0
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-12",
            0
          ],
          "source": [
            "obj-8",
            1
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-14",
            0
          ],
          "source": [
            "obj-8",
            2
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-16",
            0
          ],
          "source": [
            "obj-8",
            3
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-18",
            0
          ],
          "source": [
            "obj-8",
            4
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-230",
            0
          ],
          "order": 1,
          "source": [
            "obj-8",
            5
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-234",
            0
          ],
          "order": 0,
          "source": [
            "obj-8",
            5
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-236",
            0
          ],
          "order": 1,
          "source": [
            "obj-8",
            6
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-240",
            0
          ],
          "order": 0,
          "source": [
            "obj-8",
            6
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-242",
            0
          ],
          "order": 1,
          "source": [
            "obj-8",
            7
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-246",
            0
          ],
          "order": 0,
          "source": [
            "obj-8",
            7
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-248",
            0
          ],
          "order": 1,
          "source": [
            "obj-8",
            8
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-252",
            0
          ],
          "order": 0,
          "source": [
            "obj-8",
            8
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-254",
            0
          ],
          "order": 1,
          "source": [
            "obj-8",
            9
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-258",
            0
          ],
          "order": 0,
          "source": [
            "obj-8",
            9
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-260",
            0
          ],
          "order": 1,
          "source": [
            "obj-8",
            10
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-264",
            0
          ],
          "order": 0,
          "source": [
            "obj-8",
            10
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-266",
            0
          ],
          "order": 1,
          "source": [
            "obj-8",
            11
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-270",
            0
          ],
          "order": 0,
          "source": [
            "obj-8",
            11
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-272",
            0
          ],
          "order": 1,
          "source": [
            "obj-8",
            12
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-276",
            0
          ],
          "order": 0,
          "source": [
            "obj-8",
            12
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-278",
            0
          ],
          "order": 1,
          "source": [
            "obj-8",
            13
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-282",
            0
          ],
          "order": 0,
          "source": [
            "obj-8",
            13
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-284",
            0
          ],
          "order": 1,
          "source": [
            "obj-8",
            14
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-288",
            0
          ],
          "order": 0,
          "source": [
            "obj-8",
            14
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-290",
            0
          ],
          "order": 1,
          "source": [
            "obj-8",
            15
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-294",
            0
          ],
          "order": 0,
          "source": [
            "obj-8",
            15
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-296",
            0
          ],
          "order": 1,
          "source": [
            "obj-8",
            16
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-300",
            0
          ],
          "order": 0,
          "source": [
            "obj-8",
            16
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-302",
            0
          ],
          "order": 1,
          "source": [
            "obj-8",
            17
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-306",
            0
          ],
          "order": 0,
          "source": [
            "obj-8",
            17
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-308",
            0
          ],
          "order": 1,
          "source": [
            "obj-8",
            18
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-312",
            0
          ],
          "order": 0,
          "source": [
            "obj-8",
            18
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-314",
            0
          ],
          "order": 1,
          "source": [
            "obj-8",
            19
          ]
        }
      },
      {
        "patchline": {
          "destination": [
            "obj-318",
            0
          ],
          "order": 0,
          "source": [
            "obj-8",
            19
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-400",
            0
          ],
          "destination": [
            "obj-401",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-401",
            0
          ],
          "destination": [
            "obj-402",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-402",
            0
          ],
          "destination": [
            "obj-403",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-403",
            0
          ],
          "destination": [
            "obj-404",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-403",
            1
          ],
          "destination": [
            "obj-404",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-403",
            2
          ],
          "destination": [
            "obj-404",
            2
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-403",
            0
          ],
          "destination": [
            "obj-415",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-403",
            1
          ],
          "destination": [
            "obj-415",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-403",
            2
          ],
          "destination": [
            "obj-415",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-404",
            0
          ],
          "destination": [
            "obj-405",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-404",
            0
          ],
          "destination": [
            "obj-406",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-405",
            0
          ],
          "destination": [
            "obj-407",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-406",
            0
          ],
          "destination": [
            "obj-408",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-407",
            0
          ],
          "destination": [
            "obj-409",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-408",
            0
          ],
          "destination": [
            "obj-409",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-407",
            0
          ],
          "destination": [
            "obj-418",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-408",
            0
          ],
          "destination": [
            "obj-420",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-414",
            0
          ],
          "destination": [
            "obj-412",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-412",
            0
          ],
          "destination": [
            "obj-410",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-409",
            0
          ],
          "destination": [
            "obj-410",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-410",
            0
          ],
          "destination": [
            "obj-411",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-411",
            0
          ],
          "destination": [
            "obj-3",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-328",
            0
          ],
          "destination": [
            "obj-500",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-504",
            0
          ],
          "destination": [
            "obj-503",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-503",
            0
          ],
          "destination": [
            "obj-505",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-505",
            0
          ],
          "destination": [
            "obj-506",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-506",
            0
          ],
          "destination": [
            "obj-500",
            2
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-505",
            1
          ],
          "destination": [
            "obj-507",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-507",
            0
          ],
          "destination": [
            "obj-509",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-328",
            0
          ],
          "destination": [
            "obj-510",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-509",
            0
          ],
          "destination": [
            "obj-510",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-500",
            0
          ],
          "destination": [
            "obj-513",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-500",
            1
          ],
          "destination": [
            "obj-514",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-510",
            0
          ],
          "destination": [
            "obj-511",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-513",
            0
          ],
          "destination": [
            "obj-511",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-510",
            0
          ],
          "destination": [
            "obj-512",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-514",
            0
          ],
          "destination": [
            "obj-512",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-511",
            0
          ],
          "destination": [
            "obj-515",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-512",
            0
          ],
          "destination": [
            "obj-516",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-519",
            0
          ],
          "destination": [
            "obj-518",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-518",
            0
          ],
          "destination": [
            "obj-500",
            1
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-522",
            0
          ],
          "destination": [
            "obj-500",
            3
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-524",
            0
          ],
          "destination": [
            "obj-500",
            4
          ]
        }
      },
      {
        "patchline": {
          "source": ["obj-401", 0],
          "destination": ["obj-530", 0]
        }
      },
      {
        "patchline": {
          "source": ["obj-530", 0],
          "destination": ["obj-531", 0]
        }
      },
      {
        "patchline": {
          "source": ["obj-531", 0],
          "destination": ["obj-532", 0]
        }
      },
      {
        "patchline": {
          "source": ["obj-532", 0],
          "destination": ["obj-533", 0]
        }
      },
      {
        "patchline": {
          "source": ["obj-533", 0],
          "destination": ["obj-534", 0]
        }
      },
      {
        "patchline": {
          "source": ["obj-534", 0],
          "destination": ["obj-535", 0]
        }
      },
      {
        "patchline": {
          "source": ["obj-535", 0],
          "destination": ["obj-536", 0]
        }
      },
      {
        "patchline": {
          "source": ["obj-536", 0],
          "destination": ["obj-537", 0]
        }
      },
      {
        "patchline": {
          "source": ["obj-537", 0],
          "destination": ["obj-200", 0],
          "hidden": 1
        }
      },
      {
        "patchline": {
          "source": ["obj-536", 1],
          "destination": ["obj-546", 0]
        }
      },
      {
        "patchline": {
          "source": ["obj-531", 1],
          "destination": ["obj-538", 0]
        }
      },
      {
        "patchline": {
          "source": ["obj-538", 0],
          "destination": ["obj-539", 0]
        }
      },
      {
        "patchline": {
          "source": ["obj-539", 0],
          "destination": ["obj-540", 0]
        }
      },
      {
        "patchline": {
          "source": ["obj-540", 0],
          "destination": ["obj-541", 0]
        }
      },
      {
        "patchline": {
          "source": ["obj-541", 0],
          "destination": ["obj-542", 0]
        }
      },
      {
        "patchline": {
          "source": ["obj-542", 0],
          "destination": ["obj-200", 0],
          "hidden": 1
        }
      },
      {
        "patchline": {
          "source": ["obj-531", 2],
          "destination": ["obj-543", 0]
        }
      },
      {
        "patchline": {
          "source": ["obj-543", 0],
          "destination": ["obj-544", 0]
        }
      },
      {
        "patchline": {
          "source": ["obj-544", 0],
          "destination": ["obj-545", 0]
        }
      },
      {
        "patchline": {
          "source": ["obj-545", 0],
          "destination": ["obj-210", 0]
        }
      },
      {
        "patchline": {
          "source": ["obj-206", 0],
          "destination": ["obj-546", 1]
        }
      },
      {
        "patchline": {
          "source": ["obj-546", 0],
          "destination": ["obj-547", 0]
        }
      },
      {
        "patchline": {
          "source": ["obj-547", 0],
          "destination": ["obj-207", 0]
        }
      },
      {
        "patchline": {
          "source": ["obj-515", 0],
          "destination": ["obj-600", 0]
        }
      },
      {
        "patchline": {
          "source": ["obj-516", 0],
          "destination": ["obj-600", 1]
        }
      },
      {
        "patchline": {
          "source": ["obj-403", 0],
          "destination": ["obj-600", 2]
        }
      },
      {
        "patchline": {
          "source": ["obj-403", 1],
          "destination": ["obj-600", 3]
        }
      },
      {
        "patchline": {
          "source": ["obj-403", 2],
          "destination": ["obj-600", 4]
        }
      },
      {
        "patchline": {
          "source": ["obj-603", 0],
          "destination": ["obj-600", 5]
        }
      },
      {
        "patchline": {
          "source": ["obj-604", 0],
          "destination": ["obj-603", 0]
        }
      },
      {
        "patchline": {
          "source": ["obj-545", 0],
          "destination": ["obj-600", 6]
        }
      },
      {
        "patchline": {
          "source": ["obj-401", 0],
          "destination": ["obj-620", 0]
        }
      },
      {
        "patchline": {
          "source": ["obj-620", 0],
          "destination": ["obj-621", 0]
        }
      },
      {
        "patchline": {
          "source": ["obj-621", 0],
          "destination": ["obj-622", 0]
        }
      },
      {
        "patchline": {
          "source": ["obj-622", 0],
          "destination": ["obj-623", 0]
        }
      },
      {
        "patchline": {
          "source": ["obj-623", 0],
          "destination": ["obj-600", 7]
        }
      },
      {
        "patchline": {
          "source": ["obj-600", 0],
          "destination": ["obj-612", 0]
        }
      },
      {
        "patchline": {
          "source": ["obj-600", 1],
          "destination": ["obj-613", 0]
        }
      },
      {
        "patchline": {
          "source": ["obj-612", 0],
          "destination": ["obj-329", 0]
        }
      },
      {
        "patchline": {
          "source": ["obj-612", 0],
          "destination": ["obj-330", 0]
        }
      },
      {
        "patchline": {
          "source": ["obj-613", 0],
          "destination": ["obj-330", 1]
        }
      },
      {
        "patchline": {
          "source": ["obj-600", 2],
          "destination": ["obj-607", 0]
        }
      },
      {
        "patchline": {
          "source": ["obj-600", 3],
          "destination": ["obj-609", 0]
        }
      },
      {
        "patchline": {
          "source": ["obj-600", 4],
          "destination": ["obj-611", 0]
        }
      },
      {
        "patchline": {
          "source": ["obj-600", 5],
          "destination": ["obj-615", 0]
        }
      },
      {
        "patchline": {
          "source": ["obj-600", 6],
          "destination": ["obj-617", 0]
        }
      },
      {
        "patchline": {
          "source": ["obj-619", 0],
          "destination": ["obj-600", 8]
        }
      },
      {
        "patchline": {
          "source": ["obj-624", 0],
          "destination": ["obj-619", 0]
        }
      },
      {
        "patchline": {
          "source": ["obj-626", 0],
          "destination": ["obj-600", 9]
        }
      },
      {
        "patchline": {
          "source": ["obj-627", 0],
          "destination": ["obj-626", 0]
        }
      }
    ],
    "originid": "pat-462",
    "dependency_cache": [
      {
        "name": "bloch-harmonics-max-direct.html",
        "type": "TEXT",
        "implicit": 1
      },
      {
        "name": "qmw_bloch_convolution_ir~.maxpat",
        "type": "JSON",
        "implicit": 1
      },
      {
        "name": "qmw_bloch_spat5~.maxpat",
        "type": "JSON",
        "implicit": 1
      },
      {
        "name": "multiconvolve~.mxo",
        "type": "iLaX",
        "implicit": 1
      }
    ],
    "autosave": 0
  }
}
