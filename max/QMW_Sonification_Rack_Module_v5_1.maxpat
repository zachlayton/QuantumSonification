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
            405.0,
            228.0,
            1151.0,
            800.0
        ],
        "openinpresentation": 1,
        "gridsize": [
            15.0,
            15.0
        ],
        "boxes": [
            {
                "box": {
                    "id": "obj-27",
                    "maxclass": "comment",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [
                        280.0,
                        186.0,
                        150.0,
                        20.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        280.0,
                        185.0,
                        150.0,
                        20.0
                    ],
                    "text": "out"
                }
            },
            {
                "box": {
                    "id": "obj-26",
                    "maxclass": "comment",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [
                        280.0,
                        147.0,
                        150.0,
                        20.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        280.0,
                        149.0,
                        150.0,
                        20.0
                    ],
                    "text": "gain"
                }
            },
            {
                "box": {
                    "id": "obj-18",
                    "maxclass": "comment",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [
                        303.0,
                        125.0,
                        150.0,
                        20.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        280.0,
                        119.0,
                        150.0,
                        20.0
                    ],
                    "text": "freq"
                }
            },
            {
                "box": {
                    "id": "obj-9",
                    "linecount": 2,
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [
                        192.0,
                        514.0,
                        103.0,
                        35.0
                    ],
                    "text": "send~ qmw_spectral_L"
                }
            },
            {
                "box": {
                    "id": "obj-19",
                    "linecount": 2,
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [
                        362.0,
                        514.0,
                        103.0,
                        35.0
                    ],
                    "text": "send~ qmw_spectral_R"
                }
            },
            {
                "box": {
                    "format": 6,
                    "id": "obj-159",
                    "maxclass": "flonum",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        "bang"
                    ],
                    "parameter_enable": 0,
                    "patching_rect": [
                        930.0,
                        714.0,
                        50.0,
                        22.0
                    ]
                }
            },
            {
                "box": {
                    "format": 6,
                    "id": "obj-160",
                    "maxclass": "flonum",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        "bang"
                    ],
                    "parameter_enable": 0,
                    "patching_rect": [
                        878.0,
                        714.0,
                        50.0,
                        22.0
                    ]
                }
            },
            {
                "box": {
                    "format": 6,
                    "id": "obj-161",
                    "maxclass": "flonum",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        "bang"
                    ],
                    "parameter_enable": 0,
                    "patching_rect": [
                        815.0,
                        714.0,
                        50.0,
                        22.0
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-162",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 3,
                    "outlettype": [
                        "float",
                        "float",
                        "float"
                    ],
                    "patching_rect": [
                        850.0,
                        685.0,
                        87.0,
                        22.0
                    ],
                    "text": "unpack 0. 0. 0."
                }
            },
            {
                "box": {
                    "format": 6,
                    "id": "obj-158",
                    "maxclass": "flonum",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        "bang"
                    ],
                    "parameter_enable": 0,
                    "patching_rect": [
                        751.0,
                        714.0,
                        50.0,
                        22.0
                    ]
                }
            },
            {
                "box": {
                    "format": 6,
                    "id": "obj-157",
                    "maxclass": "flonum",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        "bang"
                    ],
                    "parameter_enable": 0,
                    "patching_rect": [
                        699.0,
                        714.0,
                        50.0,
                        22.0
                    ]
                }
            },
            {
                "box": {
                    "format": 6,
                    "id": "obj-156",
                    "maxclass": "flonum",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        "bang"
                    ],
                    "parameter_enable": 0,
                    "patching_rect": [
                        636.0,
                        714.0,
                        50.0,
                        22.0
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-154",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 3,
                    "outlettype": [
                        "float",
                        "float",
                        "float"
                    ],
                    "patching_rect": [
                        671.0,
                        685.0,
                        87.0,
                        22.0
                    ],
                    "text": "unpack 0. 0. 0."
                }
            },
            {
                "box": {
                    "id": "obj-149",
                    "linecount": 3,
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 8,
                    "outlettype": [
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        ""
                    ],
                    "patching_rect": [
                        831.0,
                        625.0,
                        148.0,
                        49.0
                    ],
                    "text": "OSC-route /bloch /length /phase /purity /entropy /speed /trail"
                }
            },
            {
                "box": {
                    "id": "obj-143",
                    "linecount": 3,
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 8,
                    "outlettype": [
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        ""
                    ],
                    "patching_rect": [
                        671.0,
                        625.0,
                        148.0,
                        49.0
                    ],
                    "text": "OSC-route /bloch /length /phase /purity /entropy /speed /trail"
                }
            },
            {
                "box": {
                    "id": "obj-124",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 5,
                    "outlettype": [
                        "",
                        "",
                        "",
                        "",
                        ""
                    ],
                    "patching_rect": [
                        713.0,
                        577.0,
                        157.0,
                        22.0
                    ],
                    "text": "OSC-route /q0 /q1 /q2 /q3"
                }
            },
            {
                "box": {
                    "id": "obj-123",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        ""
                    ],
                    "patching_rect": [
                        713.0,
                        523.0,
                        95.0,
                        22.0
                    ],
                    "text": "OSC-route /spin"
                }
            },
            {
                "box": {
                    "id": "obj-122",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        ""
                    ],
                    "patching_rect": [
                        845.0,
                        272.0,
                        113.0,
                        22.0
                    ],
                    "text": "OSC-route /velocity"
                }
            },
            {
                "box": {
                    "id": "obj-121",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        ""
                    ],
                    "patching_rect": [
                        845.0,
                        244.0,
                        95.0,
                        22.0
                    ],
                    "text": "OSC-route /pilot"
                }
            },
            {
                "box": {
                    "format": 6,
                    "id": "obj-104",
                    "maxclass": "flonum",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        "bang"
                    ],
                    "parameter_enable": 0,
                    "patching_rect": [
                        1054.0,
                        202.0,
                        50.0,
                        22.0
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-78",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        973.0,
                        246.0,
                        137.0,
                        22.0
                    ],
                    "text": "prepend fast_decay_ms"
                }
            },
            {
                "box": {
                    "format": 6,
                    "id": "obj-70",
                    "maxclass": "flonum",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        "bang"
                    ],
                    "parameter_enable": 0,
                    "patching_rect": [
                        831.0,
                        320.0,
                        50.0,
                        22.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        139.0,
                        38.0,
                        50.0,
                        22.0
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-71",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        808.0,
                        352.0,
                        130.0,
                        22.0
                    ],
                    "text": "prepend output_ceiling"
                }
            },
            {
                "box": {
                    "id": "obj-50",
                    "maxclass": "message",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        803.0,
                        213.0,
                        50.0,
                        22.0
                    ],
                    "text": "-0."
                }
            },
            {
                "box": {
                    "format": 6,
                    "id": "obj-45",
                    "maxclass": "flonum",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        "bang"
                    ],
                    "parameter_enable": 0,
                    "patching_rect": [
                        803.0,
                        179.0,
                        50.0,
                        22.0
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-36",
                    "linecount": 2,
                    "maxclass": "message",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        670.5,
                        212.5,
                        50.0,
                        35.0
                    ],
                    "text": "11.528527"
                }
            },
            {
                "box": {
                    "id": "obj-24",
                    "logfreq": 1,
                    "maxclass": "spectroscope~",
                    "monochrome": 0,
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        462.0,
                        698.0,
                        130.0,
                        120.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        455.0,
                        356.0,
                        130.0,
                        120.0
                    ],
                    "sono": 1
                }
            },
            {
                "box": {
                    "id": "obj-25",
                    "logfreq": 1,
                    "maxclass": "spectroscope~",
                    "monochrome": 0,
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        324.0,
                        698.0,
                        130.0,
                        120.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        317.0,
                        356.0,
                        130.0,
                        120.0
                    ],
                    "sono": 1
                }
            },
            {
                "box": {
                    "id": "obj-23",
                    "logfreq": 1,
                    "maxclass": "spectroscope~",
                    "monochrome": 0,
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        187.0,
                        697.0,
                        130.0,
                        120.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        180.0,
                        355.0,
                        130.0,
                        120.0
                    ],
                    "sono": 1
                }
            },
            {
                "box": {
                    "id": "obj-20",
                    "logfreq": 1,
                    "maxclass": "spectroscope~",
                    "monochrome": 0,
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        42.0,
                        697.0,
                        130.0,
                        120.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        35.0,
                        355.0,
                        130.0,
                        120.0
                    ],
                    "sono": 1
                }
            },
            {
                "box": {
                    "id": "obj-7",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        573.0,
                        171.0,
                        112.0,
                        22.0
                    ],
                    "text": "prepend coherence"
                }
            },
            {
                "box": {
                    "id": "obj-6",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        467.16666865348816,
                        171.0,
                        96.0,
                        22.0
                    ],
                    "text": "prepend entropy"
                }
            },
            {
                "box": {
                    "id": "obj-106",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        734.0,
                        309.0,
                        79.0,
                        22.0
                    ],
                    "text": "prepend amp"
                }
            },
            {
                "box": {
                    "format": 6,
                    "id": "obj-107",
                    "maxclass": "flonum",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        "bang"
                    ],
                    "parameter_enable": 0,
                    "patching_rect": [
                        763.0,
                        272.0,
                        50.0,
                        22.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        228.0,
                        148.0,
                        50.0,
                        22.0
                    ]
                }
            },
            {
                "box": {
                    "code": "// QMW Density Field Quantum Resonator 16\n//\n// Gen~ codebox.\n// in1 is the carrier frequency in Hz.\n// m0..m15 excite sixteen resonant partials.\n// ph0..ph15 set smoothed per-partial timing/phase.\n// s0..s15 set lifetime: fast lanes flash, slow lanes ring.\n// h0..h15 are partial ratios. Defaults are harmonic 1..16, but these can\n// later be replaced by Hamiltonian energy-gap ratios.\n\nParam m0(0);\nParam m1(0);\nParam m2(0);\nParam m3(0);\nParam m4(0);\nParam m5(0);\nParam m6(0);\nParam m7(0);\nParam m8(0);\nParam m9(0);\nParam m10(0);\nParam m11(0);\nParam m12(0);\nParam m13(0);\nParam m14(0);\nParam m15(0);\n\nParam ph0(0);\nParam ph1(0);\nParam ph2(0);\nParam ph3(0);\nParam ph4(0);\nParam ph5(0);\nParam ph6(0);\nParam ph7(0);\nParam ph8(0);\nParam ph9(0);\nParam ph10(0);\nParam ph11(0);\nParam ph12(0);\nParam ph13(0);\nParam ph14(0);\nParam ph15(0);\n\nParam s0(0);\nParam s1(0);\nParam s2(0);\nParam s3(0);\nParam s4(0);\nParam s5(0);\nParam s6(0);\nParam s7(0);\nParam s8(0);\nParam s9(0);\nParam s10(0);\nParam s11(0);\nParam s12(0);\nParam s13(0);\nParam s14(0);\nParam s15(0);\n\nParam h0(1);\nParam h1(2);\nParam h2(3);\nParam h3(4);\nParam h4(5);\nParam h5(6);\nParam h6(7);\nParam h7(8);\nParam h8(9);\nParam h9(10);\nParam h10(11);\nParam h11(12);\nParam h12(13);\nParam h13(14);\nParam h14(15);\nParam h15(16);\n\nParam purity(1);\nParam entropy(0);\nParam coherence(0);\nParam amp(0.2);\nParam default_freq(55);\nParam attack_ms(350);\nParam slow_decay_ms(3500);\nParam fast_decay_ms(900);\nParam phase_smooth_ms(4000);\nParam magnitude_smooth_ms(2500);\nParam brightness(0.65);\nParam mix_voices(4);\nParam output_ceiling(0.85);\nParam noise_resonator_mix(0.45);\nParam noise_amount(0.28);\nParam noise_floor(0);\nParam noise_color(0.72);\nParam noise_decay_ms(45);\nParam noise_spectral_amount(0.75);\nParam noise_spectral_gain(2.5);\nParam noise_spectral_base_hz(55);\nParam noise_spectral_q(7);\nParam quantum_pulse(0);\nParam quantum_noise_variation(0.25);\nParam quantum_brightness(0.5);\nParam quantum_event_decay_ms(1200);\nHistory quantum_pulse_z(0);\nHistory quantum_event_env(0);\nHistory modal_noise_lp(0);\nHistory nb0(0); History nl0(0);\nHistory nb1(0); History nl1(0);\nHistory nb2(0); History nl2(0);\nHistory nb3(0); History nl3(0);\nHistory nb4(0); History nl4(0);\nHistory nb5(0); History nl5(0);\nHistory nb6(0); History nl6(0);\nHistory nb7(0); History nl7(0);\nHistory nb8(0); History nl8(0);\nHistory nb9(0); History nl9(0);\nHistory nb10(0); History nl10(0);\nHistory nb11(0); History nl11(0);\nHistory nb12(0); History nl12(0);\nHistory nb13(0); History nl13(0);\nHistory nb14(0); History nl14(0);\nHistory nb15(0); History nl15(0);\n\nHistory p0(0);\nHistory p1(0);\nHistory p2(0);\nHistory p3(0);\nHistory p4(0);\nHistory p5(0);\nHistory p6(0);\nHistory p7(0);\nHistory p8(0);\nHistory p9(0);\nHistory p10(0);\nHistory p11(0);\nHistory p12(0);\nHistory p13(0);\nHistory p14(0);\nHistory p15(0);\n\nHistory e0(0);\nHistory e1(0);\nHistory e2(0);\nHistory e3(0);\nHistory e4(0);\nHistory e5(0);\nHistory e6(0);\nHistory e7(0);\nHistory e8(0);\nHistory e9(0);\nHistory e10(0);\nHistory e11(0);\nHistory e12(0);\nHistory e13(0);\nHistory e14(0);\nHistory e15(0);\n\nHistory sm0(0);\nHistory sm1(0);\nHistory sm2(0);\nHistory sm3(0);\nHistory sm4(0);\nHistory sm5(0);\nHistory sm6(0);\nHistory sm7(0);\nHistory sm8(0);\nHistory sm9(0);\nHistory sm10(0);\nHistory sm11(0);\nHistory sm12(0);\nHistory sm13(0);\nHistory sm14(0);\nHistory sm15(0);\n\nHistory sph0(0);\nHistory sph1(0);\nHistory sph2(0);\nHistory sph3(0);\nHistory sph4(0);\nHistory sph5(0);\nHistory sph6(0);\nHistory sph7(0);\nHistory sph8(0);\nHistory sph9(0);\nHistory sph10(0);\nHistory sph11(0);\nHistory sph12(0);\nHistory sph13(0);\nHistory sph14(0);\nHistory sph15(0);\n\nfreq = (in1 > 0) * in1 + (in1 <= 0) * default_freq;\npur = clamp(purity, 0, 1);\nent = clamp(entropy, 0, 1);\ncoh = clamp(coherence, 0, 1);\n\nmag_ms = max(magnitude_smooth_ms, 0.1);\nmag_coeff = exp(-1 / (mag_ms * 0.001 * samplerate));\n\ntm0 = clamp(m0, 0, 1);\ntm1 = clamp(m1, 0, 1);\ntm2 = clamp(m2, 0, 1);\ntm3 = clamp(m3, 0, 1);\ntm4 = clamp(m4, 0, 1);\ntm5 = clamp(m5, 0, 1);\ntm6 = clamp(m6, 0, 1);\ntm7 = clamp(m7, 0, 1);\ntm8 = clamp(m8, 0, 1);\ntm9 = clamp(m9, 0, 1);\ntm10 = clamp(m10, 0, 1);\ntm11 = clamp(m11, 0, 1);\ntm12 = clamp(m12, 0, 1);\ntm13 = clamp(m13, 0, 1);\ntm14 = clamp(m14, 0, 1);\ntm15 = clamp(m15, 0, 1);\n\nsm0 = tm0 + mag_coeff * (sm0 - tm0);\nsm1 = tm1 + mag_coeff * (sm1 - tm1);\nsm2 = tm2 + mag_coeff * (sm2 - tm2);\nsm3 = tm3 + mag_coeff * (sm3 - tm3);\nsm4 = tm4 + mag_coeff * (sm4 - tm4);\nsm5 = tm5 + mag_coeff * (sm5 - tm5);\nsm6 = tm6 + mag_coeff * (sm6 - tm6);\nsm7 = tm7 + mag_coeff * (sm7 - tm7);\nsm8 = tm8 + mag_coeff * (sm8 - tm8);\nsm9 = tm9 + mag_coeff * (sm9 - tm9);\nsm10 = tm10 + mag_coeff * (sm10 - tm10);\nsm11 = tm11 + mag_coeff * (sm11 - tm11);\nsm12 = tm12 + mag_coeff * (sm12 - tm12);\nsm13 = tm13 + mag_coeff * (sm13 - tm13);\nsm14 = tm14 + mag_coeff * (sm14 - tm14);\nsm15 = tm15 + mag_coeff * (sm15 - tm15);\n\nphase_ms = max(phase_smooth_ms, 0.1);\nphase_coeff = exp(-1 / (phase_ms * 0.001 * samplerate));\n\ndph0 = atan2(sin(ph0 - sph0), cos(ph0 - sph0));\ndph1 = atan2(sin(ph1 - sph1), cos(ph1 - sph1));\ndph2 = atan2(sin(ph2 - sph2), cos(ph2 - sph2));\ndph3 = atan2(sin(ph3 - sph3), cos(ph3 - sph3));\ndph4 = atan2(sin(ph4 - sph4), cos(ph4 - sph4));\ndph5 = atan2(sin(ph5 - sph5), cos(ph5 - sph5));\ndph6 = atan2(sin(ph6 - sph6), cos(ph6 - sph6));\ndph7 = atan2(sin(ph7 - sph7), cos(ph7 - sph7));\ndph8 = atan2(sin(ph8 - sph8), cos(ph8 - sph8));\ndph9 = atan2(sin(ph9 - sph9), cos(ph9 - sph9));\ndph10 = atan2(sin(ph10 - sph10), cos(ph10 - sph10));\ndph11 = atan2(sin(ph11 - sph11), cos(ph11 - sph11));\ndph12 = atan2(sin(ph12 - sph12), cos(ph12 - sph12));\ndph13 = atan2(sin(ph13 - sph13), cos(ph13 - sph13));\ndph14 = atan2(sin(ph14 - sph14), cos(ph14 - sph14));\ndph15 = atan2(sin(ph15 - sph15), cos(ph15 - sph15));\n\nsph0 = sph0 + (1 - phase_coeff) * dph0;\nsph1 = sph1 + (1 - phase_coeff) * dph1;\nsph2 = sph2 + (1 - phase_coeff) * dph2;\nsph3 = sph3 + (1 - phase_coeff) * dph3;\nsph4 = sph4 + (1 - phase_coeff) * dph4;\nsph5 = sph5 + (1 - phase_coeff) * dph5;\nsph6 = sph6 + (1 - phase_coeff) * dph6;\nsph7 = sph7 + (1 - phase_coeff) * dph7;\nsph8 = sph8 + (1 - phase_coeff) * dph8;\nsph9 = sph9 + (1 - phase_coeff) * dph9;\nsph10 = sph10 + (1 - phase_coeff) * dph10;\nsph11 = sph11 + (1 - phase_coeff) * dph11;\nsph12 = sph12 + (1 - phase_coeff) * dph12;\nsph13 = sph13 + (1 - phase_coeff) * dph13;\nsph14 = sph14 + (1 - phase_coeff) * dph14;\nsph15 = sph15 + (1 - phase_coeff) * dph15;\n\natk_ms = max(attack_ms * mix(1.35, 0.65, coh), 0.1);\natk_coeff = exp(-1 / (atk_ms * 0.001 * samplerate));\n\nspd0 = clamp(abs(s0), 0, 1);\nspd1 = clamp(abs(s1), 0, 1);\nspd2 = clamp(abs(s2), 0, 1);\nspd3 = clamp(abs(s3), 0, 1);\nspd4 = clamp(abs(s4), 0, 1);\nspd5 = clamp(abs(s5), 0, 1);\nspd6 = clamp(abs(s6), 0, 1);\nspd7 = clamp(abs(s7), 0, 1);\nspd8 = clamp(abs(s8), 0, 1);\nspd9 = clamp(abs(s9), 0, 1);\nspd10 = clamp(abs(s10), 0, 1);\nspd11 = clamp(abs(s11), 0, 1);\nspd12 = clamp(abs(s12), 0, 1);\nspd13 = clamp(abs(s13), 0, 1);\nspd14 = clamp(abs(s14), 0, 1);\nspd15 = clamp(abs(s15), 0, 1);\n\ndec0 = mix(slow_decay_ms, fast_decay_ms, spd0);\ndec1 = mix(slow_decay_ms, fast_decay_ms, spd1);\ndec2 = mix(slow_decay_ms, fast_decay_ms, spd2);\ndec3 = mix(slow_decay_ms, fast_decay_ms, spd3);\ndec4 = mix(slow_decay_ms, fast_decay_ms, spd4);\ndec5 = mix(slow_decay_ms, fast_decay_ms, spd5);\ndec6 = mix(slow_decay_ms, fast_decay_ms, spd6);\ndec7 = mix(slow_decay_ms, fast_decay_ms, spd7);\ndec8 = mix(slow_decay_ms, fast_decay_ms, spd8);\ndec9 = mix(slow_decay_ms, fast_decay_ms, spd9);\ndec10 = mix(slow_decay_ms, fast_decay_ms, spd10);\ndec11 = mix(slow_decay_ms, fast_decay_ms, spd11);\ndec12 = mix(slow_decay_ms, fast_decay_ms, spd12);\ndec13 = mix(slow_decay_ms, fast_decay_ms, spd13);\ndec14 = mix(slow_decay_ms, fast_decay_ms, spd14);\ndec15 = mix(slow_decay_ms, fast_decay_ms, spd15);\n\ndc0 = exp(-1 / (max(dec0, 0.1) * 0.001 * samplerate));\ndc1 = exp(-1 / (max(dec1, 0.1) * 0.001 * samplerate));\ndc2 = exp(-1 / (max(dec2, 0.1) * 0.001 * samplerate));\ndc3 = exp(-1 / (max(dec3, 0.1) * 0.001 * samplerate));\ndc4 = exp(-1 / (max(dec4, 0.1) * 0.001 * samplerate));\ndc5 = exp(-1 / (max(dec5, 0.1) * 0.001 * samplerate));\ndc6 = exp(-1 / (max(dec6, 0.1) * 0.001 * samplerate));\ndc7 = exp(-1 / (max(dec7, 0.1) * 0.001 * samplerate));\ndc8 = exp(-1 / (max(dec8, 0.1) * 0.001 * samplerate));\ndc9 = exp(-1 / (max(dec9, 0.1) * 0.001 * samplerate));\ndc10 = exp(-1 / (max(dec10, 0.1) * 0.001 * samplerate));\ndc11 = exp(-1 / (max(dec11, 0.1) * 0.001 * samplerate));\ndc12 = exp(-1 / (max(dec12, 0.1) * 0.001 * samplerate));\ndc13 = exp(-1 / (max(dec13, 0.1) * 0.001 * samplerate));\ndc14 = exp(-1 / (max(dec14, 0.1) * 0.001 * samplerate));\ndc15 = exp(-1 / (max(dec15, 0.1) * 0.001 * samplerate));\n\n// Higher entropy lifts weaker modes. Higher purity makes excitation more selective.\nexc_shape = mix(0.55, 1.6, pur);\nt0 = pow(sm0 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt1 = pow(sm1 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt2 = pow(sm2 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt3 = pow(sm3 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt4 = pow(sm4 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt5 = pow(sm5 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt6 = pow(sm6 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt7 = pow(sm7 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt8 = pow(sm8 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt9 = pow(sm9 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt10 = pow(sm10 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt11 = pow(sm11 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt12 = pow(sm12 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt13 = pow(sm13 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt14 = pow(sm14 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt15 = pow(sm15 + 0.00001, exc_shape) * mix(0.35, 1, ent);\n\ne0 = (t0 > e0) * (t0 + atk_coeff * (e0 - t0)) + (t0 <= e0) * (t0 + dc0 * (e0 - t0));\ne1 = (t1 > e1) * (t1 + atk_coeff * (e1 - t1)) + (t1 <= e1) * (t1 + dc1 * (e1 - t1));\ne2 = (t2 > e2) * (t2 + atk_coeff * (e2 - t2)) + (t2 <= e2) * (t2 + dc2 * (e2 - t2));\ne3 = (t3 > e3) * (t3 + atk_coeff * (e3 - t3)) + (t3 <= e3) * (t3 + dc3 * (e3 - t3));\ne4 = (t4 > e4) * (t4 + atk_coeff * (e4 - t4)) + (t4 <= e4) * (t4 + dc4 * (e4 - t4));\ne5 = (t5 > e5) * (t5 + atk_coeff * (e5 - t5)) + (t5 <= e5) * (t5 + dc5 * (e5 - t5));\ne6 = (t6 > e6) * (t6 + atk_coeff * (e6 - t6)) + (t6 <= e6) * (t6 + dc6 * (e6 - t6));\ne7 = (t7 > e7) * (t7 + atk_coeff * (e7 - t7)) + (t7 <= e7) * (t7 + dc7 * (e7 - t7));\ne8 = (t8 > e8) * (t8 + atk_coeff * (e8 - t8)) + (t8 <= e8) * (t8 + dc8 * (e8 - t8));\ne9 = (t9 > e9) * (t9 + atk_coeff * (e9 - t9)) + (t9 <= e9) * (t9 + dc9 * (e9 - t9));\ne10 = (t10 > e10) * (t10 + atk_coeff * (e10 - t10)) + (t10 <= e10) * (t10 + dc10 * (e10 - t10));\ne11 = (t11 > e11) * (t11 + atk_coeff * (e11 - t11)) + (t11 <= e11) * (t11 + dc11 * (e11 - t11));\ne12 = (t12 > e12) * (t12 + atk_coeff * (e12 - t12)) + (t12 <= e12) * (t12 + dc12 * (e12 - t12));\ne13 = (t13 > e13) * (t13 + atk_coeff * (e13 - t13)) + (t13 <= e13) * (t13 + dc13 * (e13 - t13));\ne14 = (t14 > e14) * (t14 + atk_coeff * (e14 - t14)) + (t14 <= e14) * (t14 + dc14 * (e14 - t14));\ne15 = (t15 > e15) * (t15 + atk_coeff * (e15 - t15)) + (t15 <= e15) * (t15 + dc15 * (e15 - t15));\n\nbright = clamp(brightness + ent * 0.18 + (quantum_brightness - 0.5) * 0.55, 0, 1);\n\np0 = fract(p0 + freq * max(h0, 0.01) / samplerate);\np1 = fract(p1 + freq * max(h1, 0.01) / samplerate);\np2 = fract(p2 + freq * max(h2, 0.01) / samplerate);\np3 = fract(p3 + freq * max(h3, 0.01) / samplerate);\np4 = fract(p4 + freq * max(h4, 0.01) / samplerate);\np5 = fract(p5 + freq * max(h5, 0.01) / samplerate);\np6 = fract(p6 + freq * max(h6, 0.01) / samplerate);\np7 = fract(p7 + freq * max(h7, 0.01) / samplerate);\np8 = fract(p8 + freq * max(h8, 0.01) / samplerate);\np9 = fract(p9 + freq * max(h9, 0.01) / samplerate);\np10 = fract(p10 + freq * max(h10, 0.01) / samplerate);\np11 = fract(p11 + freq * max(h11, 0.01) / samplerate);\np12 = fract(p12 + freq * max(h12, 0.01) / samplerate);\np13 = fract(p13 + freq * max(h13, 0.01) / samplerate);\np14 = fract(p14 + freq * max(h14, 0.01) / samplerate);\np15 = fract(p15 + freq * max(h15, 0.01) / samplerate);\n\ntwopi = 6.283185307179586;\npartials =\n    e0 * sin(twopi * p0 + sph0) / pow(max(h0, 1), bright) +\n    e1 * sin(twopi * p1 + sph1) / pow(max(h1, 1), bright) +\n    e2 * sin(twopi * p2 + sph2) / pow(max(h2, 1), bright) +\n    e3 * sin(twopi * p3 + sph3) / pow(max(h3, 1), bright) +\n    e4 * sin(twopi * p4 + sph4) / pow(max(h4, 1), bright) +\n    e5 * sin(twopi * p5 + sph5) / pow(max(h5, 1), bright) +\n    e6 * sin(twopi * p6 + sph6) / pow(max(h6, 1), bright) +\n    e7 * sin(twopi * p7 + sph7) / pow(max(h7, 1), bright) +\n    e8 * sin(twopi * p8 + sph8) / pow(max(h8, 1), bright) +\n    e9 * sin(twopi * p9 + sph9) / pow(max(h9, 1), bright) +\n    e10 * sin(twopi * p10 + sph10) / pow(max(h10, 1), bright) +\n    e11 * sin(twopi * p11 + sph11) / pow(max(h11, 1), bright) +\n    e12 * sin(twopi * p12 + sph12) / pow(max(h12, 1), bright) +\n    e13 * sin(twopi * p13 + sph13) / pow(max(h13, 1), bright) +\n    e14 * sin(twopi * p14 + sph14) / pow(max(h14, 1), bright) +\n    e15 * sin(twopi * p15 + sph15) / pow(max(h15, 1), bright);\n\nraw_modal_noise = noise();\nnoise_color_coeff = exp(-1 / (max(noise_decay_ms, 0.1) * 0.001 * samplerate));\nmodal_noise_lp = raw_modal_noise + noise_color_coeff * (modal_noise_lp - raw_modal_noise);\ncolored_modal_noise = mix(modal_noise_lp, raw_modal_noise, clamp(noise_color, 0, 1));\nquantum_trigger = (quantum_pulse > 0.5) * (quantum_pulse_z <= 0.5);\nquantum_pulse_z = quantum_pulse;\nquantum_decay_coeff = exp(-1 / (max(quantum_event_decay_ms, 1) * 0.001 * samplerate));\nquantum_event_env = quantum_trigger + (1 - quantum_trigger) * quantum_event_env * quantum_decay_coeff;\nnoise_level = (clamp(noise_floor, 0, 0.25) + 0.25 * clamp(noise_amount, 0, 1))\n    * clamp(quantum_noise_variation, 0, 1)\n    * (0.06 + 0.94 * clamp(quantum_event_env, 0, 1));\nnoise_input = colored_modal_noise * noise_level;\nmodal_q_eff = clamp(noise_spectral_q * 4 * mix(0.72, 1.45, pur), 2, 120);\nnf0 = clamp(freq * max(h0, 0.01), max(20, noise_spectral_base_hz * 0.25), samplerate * 0.45);\nng0 = tan(3.141592653589793 * nf0 / samplerate);\nna0 = 1 / (1 + ng0 * (ng0 + 1 / modal_q_eff));\nnv0 = na0 * (nb0 + ng0 * (noise_input - nl0));\nnlv0 = nl0 + ng0 * nv0;\nnb0 = 2 * nv0 - nb0;\nnl0 = 2 * nlv0 - nl0;\nnf1 = clamp(freq * max(h1, 0.01), max(20, noise_spectral_base_hz * 0.25), samplerate * 0.45);\nng1 = tan(3.141592653589793 * nf1 / samplerate);\nna1 = 1 / (1 + ng1 * (ng1 + 1 / modal_q_eff));\nnv1 = na1 * (nb1 + ng1 * (noise_input - nl1));\nnlv1 = nl1 + ng1 * nv1;\nnb1 = 2 * nv1 - nb1;\nnl1 = 2 * nlv1 - nl1;\nnf2 = clamp(freq * max(h2, 0.01), max(20, noise_spectral_base_hz * 0.25), samplerate * 0.45);\nng2 = tan(3.141592653589793 * nf2 / samplerate);\nna2 = 1 / (1 + ng2 * (ng2 + 1 / modal_q_eff));\nnv2 = na2 * (nb2 + ng2 * (noise_input - nl2));\nnlv2 = nl2 + ng2 * nv2;\nnb2 = 2 * nv2 - nb2;\nnl2 = 2 * nlv2 - nl2;\nnf3 = clamp(freq * max(h3, 0.01), max(20, noise_spectral_base_hz * 0.25), samplerate * 0.45);\nng3 = tan(3.141592653589793 * nf3 / samplerate);\nna3 = 1 / (1 + ng3 * (ng3 + 1 / modal_q_eff));\nnv3 = na3 * (nb3 + ng3 * (noise_input - nl3));\nnlv3 = nl3 + ng3 * nv3;\nnb3 = 2 * nv3 - nb3;\nnl3 = 2 * nlv3 - nl3;\nnf4 = clamp(freq * max(h4, 0.01), max(20, noise_spectral_base_hz * 0.25), samplerate * 0.45);\nng4 = tan(3.141592653589793 * nf4 / samplerate);\nna4 = 1 / (1 + ng4 * (ng4 + 1 / modal_q_eff));\nnv4 = na4 * (nb4 + ng4 * (noise_input - nl4));\nnlv4 = nl4 + ng4 * nv4;\nnb4 = 2 * nv4 - nb4;\nnl4 = 2 * nlv4 - nl4;\nnf5 = clamp(freq * max(h5, 0.01), max(20, noise_spectral_base_hz * 0.25), samplerate * 0.45);\nng5 = tan(3.141592653589793 * nf5 / samplerate);\nna5 = 1 / (1 + ng5 * (ng5 + 1 / modal_q_eff));\nnv5 = na5 * (nb5 + ng5 * (noise_input - nl5));\nnlv5 = nl5 + ng5 * nv5;\nnb5 = 2 * nv5 - nb5;\nnl5 = 2 * nlv5 - nl5;\nnf6 = clamp(freq * max(h6, 0.01), max(20, noise_spectral_base_hz * 0.25), samplerate * 0.45);\nng6 = tan(3.141592653589793 * nf6 / samplerate);\nna6 = 1 / (1 + ng6 * (ng6 + 1 / modal_q_eff));\nnv6 = na6 * (nb6 + ng6 * (noise_input - nl6));\nnlv6 = nl6 + ng6 * nv6;\nnb6 = 2 * nv6 - nb6;\nnl6 = 2 * nlv6 - nl6;\nnf7 = clamp(freq * max(h7, 0.01), max(20, noise_spectral_base_hz * 0.25), samplerate * 0.45);\nng7 = tan(3.141592653589793 * nf7 / samplerate);\nna7 = 1 / (1 + ng7 * (ng7 + 1 / modal_q_eff));\nnv7 = na7 * (nb7 + ng7 * (noise_input - nl7));\nnlv7 = nl7 + ng7 * nv7;\nnb7 = 2 * nv7 - nb7;\nnl7 = 2 * nlv7 - nl7;\nnf8 = clamp(freq * max(h8, 0.01), max(20, noise_spectral_base_hz * 0.25), samplerate * 0.45);\nng8 = tan(3.141592653589793 * nf8 / samplerate);\nna8 = 1 / (1 + ng8 * (ng8 + 1 / modal_q_eff));\nnv8 = na8 * (nb8 + ng8 * (noise_input - nl8));\nnlv8 = nl8 + ng8 * nv8;\nnb8 = 2 * nv8 - nb8;\nnl8 = 2 * nlv8 - nl8;\nnf9 = clamp(freq * max(h9, 0.01), max(20, noise_spectral_base_hz * 0.25), samplerate * 0.45);\nng9 = tan(3.141592653589793 * nf9 / samplerate);\nna9 = 1 / (1 + ng9 * (ng9 + 1 / modal_q_eff));\nnv9 = na9 * (nb9 + ng9 * (noise_input - nl9));\nnlv9 = nl9 + ng9 * nv9;\nnb9 = 2 * nv9 - nb9;\nnl9 = 2 * nlv9 - nl9;\nnf10 = clamp(freq * max(h10, 0.01), max(20, noise_spectral_base_hz * 0.25), samplerate * 0.45);\nng10 = tan(3.141592653589793 * nf10 / samplerate);\nna10 = 1 / (1 + ng10 * (ng10 + 1 / modal_q_eff));\nnv10 = na10 * (nb10 + ng10 * (noise_input - nl10));\nnlv10 = nl10 + ng10 * nv10;\nnb10 = 2 * nv10 - nb10;\nnl10 = 2 * nlv10 - nl10;\nnf11 = clamp(freq * max(h11, 0.01), max(20, noise_spectral_base_hz * 0.25), samplerate * 0.45);\nng11 = tan(3.141592653589793 * nf11 / samplerate);\nna11 = 1 / (1 + ng11 * (ng11 + 1 / modal_q_eff));\nnv11 = na11 * (nb11 + ng11 * (noise_input - nl11));\nnlv11 = nl11 + ng11 * nv11;\nnb11 = 2 * nv11 - nb11;\nnl11 = 2 * nlv11 - nl11;\nnf12 = clamp(freq * max(h12, 0.01), max(20, noise_spectral_base_hz * 0.25), samplerate * 0.45);\nng12 = tan(3.141592653589793 * nf12 / samplerate);\nna12 = 1 / (1 + ng12 * (ng12 + 1 / modal_q_eff));\nnv12 = na12 * (nb12 + ng12 * (noise_input - nl12));\nnlv12 = nl12 + ng12 * nv12;\nnb12 = 2 * nv12 - nb12;\nnl12 = 2 * nlv12 - nl12;\nnf13 = clamp(freq * max(h13, 0.01), max(20, noise_spectral_base_hz * 0.25), samplerate * 0.45);\nng13 = tan(3.141592653589793 * nf13 / samplerate);\nna13 = 1 / (1 + ng13 * (ng13 + 1 / modal_q_eff));\nnv13 = na13 * (nb13 + ng13 * (noise_input - nl13));\nnlv13 = nl13 + ng13 * nv13;\nnb13 = 2 * nv13 - nb13;\nnl13 = 2 * nlv13 - nl13;\nnf14 = clamp(freq * max(h14, 0.01), max(20, noise_spectral_base_hz * 0.25), samplerate * 0.45);\nng14 = tan(3.141592653589793 * nf14 / samplerate);\nna14 = 1 / (1 + ng14 * (ng14 + 1 / modal_q_eff));\nnv14 = na14 * (nb14 + ng14 * (noise_input - nl14));\nnlv14 = nl14 + ng14 * nv14;\nnb14 = 2 * nv14 - nb14;\nnl14 = 2 * nlv14 - nl14;\nnf15 = clamp(freq * max(h15, 0.01), max(20, noise_spectral_base_hz * 0.25), samplerate * 0.45);\nng15 = tan(3.141592653589793 * nf15 / samplerate);\nna15 = 1 / (1 + ng15 * (ng15 + 1 / modal_q_eff));\nnv15 = na15 * (nb15 + ng15 * (noise_input - nl15));\nnlv15 = nl15 + ng15 * nv15;\nnb15 = 2 * nv15 - nb15;\nnl15 = 2 * nlv15 - nl15;\nmodal_noise = (\n    e0 * nv0 +\n    e1 * nv1 +\n    e2 * nv2 +\n    e3 * nv3 +\n    e4 * nv4 +\n    e5 * nv5 +\n    e6 * nv6 +\n    e7 * nv7 +\n    e8 * nv8 +\n    e9 * nv9 +\n    e10 * nv10 +\n    e11 * nv11 +\n    e12 * nv12 +\n    e13 * nv13 +\n    e14 * nv14 +\n    e15 * nv15\n) / sqrt(16);\nmodal_noise = tanh(modal_noise * clamp(noise_spectral_gain, 0, 8));\nmodal_noise = mix(colored_modal_noise * noise_level, modal_noise, clamp(noise_spectral_amount, 0, 1));\n\nvoice_scale = 1 / sqrt(max(mix_voices, 1));\nsig = mix(partials, modal_noise, clamp(noise_resonator_mix, 0, 1));\n\nout1 = sig * amp * output_ceiling * voice_scale;\nout2 = e0 + e1 + e2 + e3 + e4 + e5 + e6 + e7 + e8 + e9 + e10 + e11 + e12 + e13 + e14 + e15;\nout3 = freq;\n",
                    "fontface": 0,
                    "fontname": "<Monospaced>",
                    "fontsize": 12.0,
                    "id": "obj-108",
                    "maxclass": "gen.codebox~",
                    "numinlets": 1,
                    "numoutlets": 3,
                    "outlettype": [
                        "signal",
                        "signal",
                        "signal"
                    ],
                    "patching_rect": [
                        680.0,
                        386.25,
                        172.0,
                        32.5
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-109",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [
                        "signal"
                    ],
                    "patching_rect": [
                        680.0,
                        309.0,
                        31.0,
                        22.0
                    ],
                    "text": "sig~"
                }
            },
            {
                "box": {
                    "format": 6,
                    "id": "obj-110",
                    "maxclass": "flonum",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        "bang"
                    ],
                    "parameter_enable": 0,
                    "patching_rect": [
                        679.0,
                        265.0,
                        50.0,
                        22.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        228.0,
                        118.0,
                        50.0,
                        22.0
                    ]
                }
            },
            {
                "box": {
                    "format": 6,
                    "id": "obj-111",
                    "maxclass": "flonum",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        "bang"
                    ],
                    "parameter_enable": 0,
                    "patching_rect": [
                        726.0,
                        442.0,
                        50.0,
                        22.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        228.0,
                        184.0,
                        50.0,
                        22.0
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-112",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        "signal"
                    ],
                    "patching_rect": [
                        680.0,
                        449.0,
                        34.0,
                        22.0
                    ],
                    "text": "*~ 1."
                }
            },
            {
                "box": {
                    "id": "obj-105",
                    "maxclass": "preset",
                    "numinlets": 1,
                    "numoutlets": 5,
                    "outlettype": [
                        "preset",
                        "int",
                        "preset",
                        "int",
                        ""
                    ],
                    "patching_rect": [
                        119.0,
                        66.0,
                        100.0,
                        40.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        119.0,
                        66.0,
                        100.0,
                        40.0
                    ],
                    "preset_data": [
                        {
                            "number": 1,
                            "data": [
                                5,
                                "obj-59",
                                "number",
                                "float",
                                0.25,
                                5,
                                "obj-75",
                                "number",
                                "float",
                                40.0,
                                5,
                                "obj-30",
                                "number",
                                "float",
                                0.25,
                                5,
                                "obj-40",
                                "number",
                                "float",
                                0.25,
                                5,
                                "obj-16",
                                "number",
                                "float",
                                0.50900000333786,
                                5,
                                "obj-58",
                                "number",
                                "float",
                                80.0,
                                5,
                                "obj-22",
                                "number",
                                "float",
                                0.684000015258789,
                                5,
                                "obj-65",
                                "number",
                                "float",
                                160.0,
                                5,
                                "obj-62",
                                "number",
                                "float",
                                0.529999971389771,
                                5,
                                "obj-111",
                                "number",
                                "float",
                                0.25,
                                5,
                                "obj-110",
                                "number",
                                "float",
                                100.0,
                                5,
                                "obj-107",
                                "number",
                                "float",
                                0.319999992847443,
                                5,
                                "obj-45",
                                "number",
                                "float",
                                1.0,
                                5,
                                "obj-70",
                                "number",
                                "float",
                                0.970000028610229,
                                5,
                                "obj-104",
                                "number",
                                "float",
                                40.0,
                                5,
                                "obj-156",
                                "number",
                                "float",
                                0.044582739472389,
                                5,
                                "obj-157",
                                "number",
                                "float",
                                -0.443708449602127,
                                5,
                                "obj-158",
                                "number",
                                "float",
                                0.093926310539246,
                                5,
                                "obj-161",
                                "number",
                                "float",
                                -0.097806394100189,
                                5,
                                "obj-160",
                                "number",
                                "float",
                                0.254380077123642,
                                5,
                                "obj-159",
                                "number",
                                "float",
                                -0.056636601686478
                            ]
                        },
                        {
                            "number": 2,
                            "data": [
                                5,
                                "obj-59",
                                "number",
                                "float",
                                0.25,
                                5,
                                "obj-75",
                                "number",
                                "float",
                                55.0,
                                5,
                                "obj-30",
                                "number",
                                "float",
                                0.25,
                                5,
                                "obj-40",
                                "number",
                                "float",
                                0.25,
                                5,
                                "obj-16",
                                "number",
                                "float",
                                0.419999986886978,
                                5,
                                "obj-58",
                                "number",
                                "float",
                                109.5999984741211,
                                5,
                                "obj-22",
                                "number",
                                "float",
                                0.551999986171722,
                                5,
                                "obj-65",
                                "number",
                                "float",
                                142.0,
                                5,
                                "obj-62",
                                "number",
                                "float",
                                0.432000011205673,
                                5,
                                "obj-111",
                                "number",
                                "float",
                                0.25,
                                5,
                                "obj-110",
                                "number",
                                "float",
                                157.10000610351562,
                                5,
                                "obj-107",
                                "number",
                                "float",
                                0.317999988794327
                            ]
                        },
                        {
                            "number": 3,
                            "data": [
                                5,
                                "obj-59",
                                "number",
                                "float",
                                0.25,
                                5,
                                "obj-75",
                                "number",
                                "float",
                                25.0,
                                5,
                                "obj-30",
                                "number",
                                "float",
                                0.25,
                                5,
                                "obj-40",
                                "number",
                                "float",
                                0.25,
                                5,
                                "obj-16",
                                "number",
                                "float",
                                1.0,
                                5,
                                "obj-58",
                                "number",
                                "float",
                                37.70000076293945,
                                5,
                                "obj-22",
                                "number",
                                "float",
                                1.0,
                                5,
                                "obj-65",
                                "number",
                                "float",
                                50.29999923706055,
                                5,
                                "obj-62",
                                "number",
                                "float",
                                1.0,
                                5,
                                "obj-111",
                                "number",
                                "float",
                                0.25,
                                5,
                                "obj-110",
                                "number",
                                "float",
                                63.0,
                                5,
                                "obj-107",
                                "number",
                                "float",
                                1.0,
                                5,
                                "obj-45",
                                "number",
                                "float",
                                1.0
                            ]
                        },
                        {
                            "number": 4,
                            "data": [
                                5,
                                "obj-59",
                                "number",
                                "float",
                                0.087999999523163,
                                5,
                                "obj-75",
                                "number",
                                "float",
                                19.799999237060547,
                                5,
                                "obj-30",
                                "number",
                                "float",
                                0.160999998450279,
                                5,
                                "obj-40",
                                "number",
                                "float",
                                0.172000005841255,
                                5,
                                "obj-16",
                                "number",
                                "float",
                                0.216999992728233,
                                5,
                                "obj-58",
                                "number",
                                "float",
                                10.420000076293945,
                                5,
                                "obj-22",
                                "number",
                                "float",
                                0.119999997317791,
                                5,
                                "obj-65",
                                "number",
                                "float",
                                29.8700008392334,
                                5,
                                "obj-62",
                                "number",
                                "float",
                                0.100000001490116,
                                5,
                                "obj-111",
                                "number",
                                "float",
                                0.020999999716878,
                                5,
                                "obj-110",
                                "number",
                                "float",
                                39.7400016784668,
                                5,
                                "obj-107",
                                "number",
                                "float",
                                0.138999998569489,
                                5,
                                "obj-45",
                                "number",
                                "float",
                                1.0,
                                5,
                                "obj-70",
                                "number",
                                "float",
                                17.799999237060547,
                                5,
                                "obj-104",
                                "number",
                                "float",
                                40.0
                            ]
                        },
                        {
                            "number": 5,
                            "data": [
                                5,
                                "obj-59",
                                "number",
                                "float",
                                0.153999999165535,
                                5,
                                "obj-75",
                                "number",
                                "float",
                                70.0,
                                5,
                                "obj-30",
                                "number",
                                "float",
                                0.25,
                                5,
                                "obj-40",
                                "number",
                                "float",
                                0.25,
                                5,
                                "obj-16",
                                "number",
                                "float",
                                0.114000000059605,
                                5,
                                "obj-58",
                                "number",
                                "float",
                                80.0,
                                5,
                                "obj-22",
                                "number",
                                "float",
                                0.119999997317791,
                                5,
                                "obj-65",
                                "number",
                                "float",
                                90.0,
                                5,
                                "obj-62",
                                "number",
                                "float",
                                0.100000001490116,
                                5,
                                "obj-111",
                                "number",
                                "float",
                                0.310000002384186,
                                5,
                                "obj-110",
                                "number",
                                "float",
                                100.0,
                                5,
                                "obj-107",
                                "number",
                                "float",
                                0.155000001192093,
                                5,
                                "obj-45",
                                "number",
                                "float",
                                1.0,
                                5,
                                "obj-70",
                                "number",
                                "float",
                                17.799999237060547,
                                5,
                                "obj-104",
                                "number",
                                "float",
                                40.0,
                                5,
                                "obj-156",
                                "number",
                                "float",
                                -0.039282333105803,
                                5,
                                "obj-157",
                                "number",
                                "float",
                                0.229355603456497,
                                5,
                                "obj-158",
                                "number",
                                "float",
                                0.001678827451542,
                                5,
                                "obj-161",
                                "number",
                                "float",
                                0.214919283986092,
                                5,
                                "obj-160",
                                "number",
                                "float",
                                -0.006861122790724,
                                5,
                                "obj-159",
                                "number",
                                "float",
                                -0.058972638100386
                            ]
                        },
                        {
                            "number": 6,
                            "data": [
                                5,
                                "obj-59",
                                "number",
                                "float",
                                0.153999999165535,
                                5,
                                "obj-75",
                                "number",
                                "float",
                                70.0,
                                5,
                                "obj-30",
                                "number",
                                "float",
                                0.25,
                                5,
                                "obj-40",
                                "number",
                                "float",
                                0.25,
                                5,
                                "obj-16",
                                "number",
                                "float",
                                0.114000000059605,
                                5,
                                "obj-58",
                                "number",
                                "float",
                                80.0,
                                5,
                                "obj-22",
                                "number",
                                "float",
                                0.119999997317791,
                                5,
                                "obj-65",
                                "number",
                                "float",
                                90.0,
                                5,
                                "obj-62",
                                "number",
                                "float",
                                0.100000001490116,
                                5,
                                "obj-111",
                                "number",
                                "float",
                                0.310000002384186,
                                5,
                                "obj-110",
                                "number",
                                "float",
                                100.0,
                                5,
                                "obj-107",
                                "number",
                                "float",
                                0.155000001192093,
                                5,
                                "obj-45",
                                "number",
                                "float",
                                1.0,
                                5,
                                "obj-70",
                                "number",
                                "float",
                                4.0,
                                5,
                                "obj-104",
                                "number",
                                "float",
                                40.0,
                                5,
                                "obj-156",
                                "number",
                                "float",
                                -0.112428441643715,
                                5,
                                "obj-157",
                                "number",
                                "float",
                                -0.118250109255314,
                                5,
                                "obj-158",
                                "number",
                                "float",
                                -0.242340460419655,
                                5,
                                "obj-161",
                                "number",
                                "float",
                                0.058394063264132,
                                5,
                                "obj-160",
                                "number",
                                "float",
                                0.113296903669834,
                                5,
                                "obj-159",
                                "number",
                                "float",
                                0.542528569698334
                            ]
                        },
                        {
                            "number": 7,
                            "data": [
                                5,
                                "obj-59",
                                "number",
                                "float",
                                0.153999999165535,
                                5,
                                "obj-75",
                                "number",
                                "float",
                                22.600000381469727,
                                5,
                                "obj-30",
                                "number",
                                "float",
                                0.25,
                                5,
                                "obj-40",
                                "number",
                                "float",
                                0.25,
                                5,
                                "obj-16",
                                "number",
                                "float",
                                0.114000000059605,
                                5,
                                "obj-58",
                                "number",
                                "float",
                                66.0,
                                5,
                                "obj-22",
                                "number",
                                "float",
                                0.119999997317791,
                                5,
                                "obj-65",
                                "number",
                                "float",
                                99.0,
                                5,
                                "obj-62",
                                "number",
                                "float",
                                0.100000001490116,
                                5,
                                "obj-111",
                                "number",
                                "float",
                                0.310000002384186,
                                5,
                                "obj-110",
                                "number",
                                "float",
                                22.1200008392334,
                                5,
                                "obj-107",
                                "number",
                                "float",
                                0.155000001192093,
                                5,
                                "obj-45",
                                "number",
                                "float",
                                1.0,
                                5,
                                "obj-70",
                                "number",
                                "float",
                                4.0,
                                5,
                                "obj-104",
                                "number",
                                "float",
                                40.0,
                                5,
                                "obj-156",
                                "number",
                                "float",
                                -0.147447824478149,
                                5,
                                "obj-157",
                                "number",
                                "float",
                                -0.513610482215881,
                                5,
                                "obj-158",
                                "number",
                                "float",
                                -0.150007009506226,
                                5,
                                "obj-161",
                                "number",
                                "float",
                                0.065598845481873,
                                5,
                                "obj-160",
                                "number",
                                "float",
                                0.469996899366379,
                                5,
                                "obj-159",
                                "number",
                                "float",
                                0.331080973148346
                            ]
                        }
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-60",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        494.0,
                        315.0,
                        79.0,
                        22.0
                    ],
                    "text": "prepend amp"
                }
            },
            {
                "box": {
                    "format": 6,
                    "id": "obj-62",
                    "maxclass": "flonum",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        "bang"
                    ],
                    "parameter_enable": 0,
                    "patching_rect": [
                        523.0,
                        278.0,
                        50.0,
                        22.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        161.0,
                        148.0,
                        50.0,
                        22.0
                    ]
                }
            },
            {
                "box": {
                    "code": "// QMW Desity Field Quantum Resonator 16\n//\n// Gen~ codebox.\n// in1 is the carrier frequency in Hz.\n// m0..m15 excite sixteen resonant partials.\n// ph0..ph15 set smoothed per-partial timing/phase.\n// s0..s15 set lifetime: fast lanes flash, slow lanes ring.\n// h0..h15 are partial ratios. Defaults are harmonic 1..16, but these can\n// later be replaced by Hamiltonian energy-gap ratios.\n\nParam m0(0);\nParam m1(0);\nParam m2(0);\nParam m3(0);\nParam m4(0);\nParam m5(0);\nParam m6(0);\nParam m7(0);\nParam m8(0);\nParam m9(0);\nParam m10(0);\nParam m11(0);\nParam m12(0);\nParam m13(0);\nParam m14(0);\nParam m15(0);\n\nParam ph0(0);\nParam ph1(0);\nParam ph2(0);\nParam ph3(0);\nParam ph4(0);\nParam ph5(0);\nParam ph6(0);\nParam ph7(0);\nParam ph8(0);\nParam ph9(0);\nParam ph10(0);\nParam ph11(0);\nParam ph12(0);\nParam ph13(0);\nParam ph14(0);\nParam ph15(0);\n\nParam s0(0);\nParam s1(0);\nParam s2(0);\nParam s3(0);\nParam s4(0);\nParam s5(0);\nParam s6(0);\nParam s7(0);\nParam s8(0);\nParam s9(0);\nParam s10(0);\nParam s11(0);\nParam s12(0);\nParam s13(0);\nParam s14(0);\nParam s15(0);\n\nParam h0(1);\nParam h1(2);\nParam h2(3);\nParam h3(4);\nParam h4(5);\nParam h5(6);\nParam h6(7);\nParam h7(8);\nParam h8(9);\nParam h9(10);\nParam h10(11);\nParam h11(12);\nParam h12(13);\nParam h13(14);\nParam h14(15);\nParam h15(16);\n\nParam purity(1);\nParam entropy(0);\nParam coherence(0);\nParam amp(0.2);\nParam default_freq(55);\nParam attack_ms(350);\nParam slow_decay_ms(3500);\nParam fast_decay_ms(900);\nParam phase_smooth_ms(4000);\nParam magnitude_smooth_ms(2500);\nParam brightness(0.65);\nParam mix_voices(4);\nParam output_ceiling(0.85);\nParam noise_resonator_mix(0.45);\nParam noise_amount(0.28);\nParam noise_floor(0);\nParam noise_color(0.72);\nParam noise_decay_ms(45);\nParam noise_spectral_amount(0.75);\nParam noise_spectral_gain(2.5);\nParam noise_spectral_base_hz(55);\nParam noise_spectral_q(7);\nParam quantum_pulse(0);\nParam quantum_noise_variation(0.25);\nParam quantum_brightness(0.5);\nParam quantum_event_decay_ms(1200);\nHistory quantum_pulse_z(0);\nHistory quantum_event_env(0);\nHistory modal_noise_lp(0);\nHistory nb0(0); History nl0(0);\nHistory nb1(0); History nl1(0);\nHistory nb2(0); History nl2(0);\nHistory nb3(0); History nl3(0);\nHistory nb4(0); History nl4(0);\nHistory nb5(0); History nl5(0);\nHistory nb6(0); History nl6(0);\nHistory nb7(0); History nl7(0);\nHistory nb8(0); History nl8(0);\nHistory nb9(0); History nl9(0);\nHistory nb10(0); History nl10(0);\nHistory nb11(0); History nl11(0);\nHistory nb12(0); History nl12(0);\nHistory nb13(0); History nl13(0);\nHistory nb14(0); History nl14(0);\nHistory nb15(0); History nl15(0);\n\nHistory p0(0);\nHistory p1(0);\nHistory p2(0);\nHistory p3(0);\nHistory p4(0);\nHistory p5(0);\nHistory p6(0);\nHistory p7(0);\nHistory p8(0);\nHistory p9(0);\nHistory p10(0);\nHistory p11(0);\nHistory p12(0);\nHistory p13(0);\nHistory p14(0);\nHistory p15(0);\n\nHistory e0(0);\nHistory e1(0);\nHistory e2(0);\nHistory e3(0);\nHistory e4(0);\nHistory e5(0);\nHistory e6(0);\nHistory e7(0);\nHistory e8(0);\nHistory e9(0);\nHistory e10(0);\nHistory e11(0);\nHistory e12(0);\nHistory e13(0);\nHistory e14(0);\nHistory e15(0);\n\nHistory sm0(0);\nHistory sm1(0);\nHistory sm2(0);\nHistory sm3(0);\nHistory sm4(0);\nHistory sm5(0);\nHistory sm6(0);\nHistory sm7(0);\nHistory sm8(0);\nHistory sm9(0);\nHistory sm10(0);\nHistory sm11(0);\nHistory sm12(0);\nHistory sm13(0);\nHistory sm14(0);\nHistory sm15(0);\n\nHistory sph0(0);\nHistory sph1(0);\nHistory sph2(0);\nHistory sph3(0);\nHistory sph4(0);\nHistory sph5(0);\nHistory sph6(0);\nHistory sph7(0);\nHistory sph8(0);\nHistory sph9(0);\nHistory sph10(0);\nHistory sph11(0);\nHistory sph12(0);\nHistory sph13(0);\nHistory sph14(0);\nHistory sph15(0);\n\nfreq = (in1 > 0) * in1 + (in1 <= 0) * default_freq;\npur = clamp(purity, 0, 1);\nent = clamp(entropy, 0, 1);\ncoh = clamp(coherence, 0, 1);\n\nmag_ms = max(magnitude_smooth_ms, 0.1);\nmag_coeff = exp(-1 / (mag_ms * 0.001 * samplerate));\n\ntm0 = clamp(m0, 0, 1);\ntm1 = clamp(m1, 0, 1);\ntm2 = clamp(m2, 0, 1);\ntm3 = clamp(m3, 0, 1);\ntm4 = clamp(m4, 0, 1);\ntm5 = clamp(m5, 0, 1);\ntm6 = clamp(m6, 0, 1);\ntm7 = clamp(m7, 0, 1);\ntm8 = clamp(m8, 0, 1);\ntm9 = clamp(m9, 0, 1);\ntm10 = clamp(m10, 0, 1);\ntm11 = clamp(m11, 0, 1);\ntm12 = clamp(m12, 0, 1);\ntm13 = clamp(m13, 0, 1);\ntm14 = clamp(m14, 0, 1);\ntm15 = clamp(m15, 0, 1);\n\nsm0 = tm0 + mag_coeff * (sm0 - tm0);\nsm1 = tm1 + mag_coeff * (sm1 - tm1);\nsm2 = tm2 + mag_coeff * (sm2 - tm2);\nsm3 = tm3 + mag_coeff * (sm3 - tm3);\nsm4 = tm4 + mag_coeff * (sm4 - tm4);\nsm5 = tm5 + mag_coeff * (sm5 - tm5);\nsm6 = tm6 + mag_coeff * (sm6 - tm6);\nsm7 = tm7 + mag_coeff * (sm7 - tm7);\nsm8 = tm8 + mag_coeff * (sm8 - tm8);\nsm9 = tm9 + mag_coeff * (sm9 - tm9);\nsm10 = tm10 + mag_coeff * (sm10 - tm10);\nsm11 = tm11 + mag_coeff * (sm11 - tm11);\nsm12 = tm12 + mag_coeff * (sm12 - tm12);\nsm13 = tm13 + mag_coeff * (sm13 - tm13);\nsm14 = tm14 + mag_coeff * (sm14 - tm14);\nsm15 = tm15 + mag_coeff * (sm15 - tm15);\n\nphase_ms = max(phase_smooth_ms, 0.1);\nphase_coeff = exp(-1 / (phase_ms * 0.001 * samplerate));\n\ndph0 = atan2(sin(ph0 - sph0), cos(ph0 - sph0));\ndph1 = atan2(sin(ph1 - sph1), cos(ph1 - sph1));\ndph2 = atan2(sin(ph2 - sph2), cos(ph2 - sph2));\ndph3 = atan2(sin(ph3 - sph3), cos(ph3 - sph3));\ndph4 = atan2(sin(ph4 - sph4), cos(ph4 - sph4));\ndph5 = atan2(sin(ph5 - sph5), cos(ph5 - sph5));\ndph6 = atan2(sin(ph6 - sph6), cos(ph6 - sph6));\ndph7 = atan2(sin(ph7 - sph7), cos(ph7 - sph7));\ndph8 = atan2(sin(ph8 - sph8), cos(ph8 - sph8));\ndph9 = atan2(sin(ph9 - sph9), cos(ph9 - sph9));\ndph10 = atan2(sin(ph10 - sph10), cos(ph10 - sph10));\ndph11 = atan2(sin(ph11 - sph11), cos(ph11 - sph11));\ndph12 = atan2(sin(ph12 - sph12), cos(ph12 - sph12));\ndph13 = atan2(sin(ph13 - sph13), cos(ph13 - sph13));\ndph14 = atan2(sin(ph14 - sph14), cos(ph14 - sph14));\ndph15 = atan2(sin(ph15 - sph15), cos(ph15 - sph15));\n\nsph0 = sph0 + (1 - phase_coeff) * dph0;\nsph1 = sph1 + (1 - phase_coeff) * dph1;\nsph2 = sph2 + (1 - phase_coeff) * dph2;\nsph3 = sph3 + (1 - phase_coeff) * dph3;\nsph4 = sph4 + (1 - phase_coeff) * dph4;\nsph5 = sph5 + (1 - phase_coeff) * dph5;\nsph6 = sph6 + (1 - phase_coeff) * dph6;\nsph7 = sph7 + (1 - phase_coeff) * dph7;\nsph8 = sph8 + (1 - phase_coeff) * dph8;\nsph9 = sph9 + (1 - phase_coeff) * dph9;\nsph10 = sph10 + (1 - phase_coeff) * dph10;\nsph11 = sph11 + (1 - phase_coeff) * dph11;\nsph12 = sph12 + (1 - phase_coeff) * dph12;\nsph13 = sph13 + (1 - phase_coeff) * dph13;\nsph14 = sph14 + (1 - phase_coeff) * dph14;\nsph15 = sph15 + (1 - phase_coeff) * dph15;\n\natk_ms = max(attack_ms * mix(1.35, 0.65, coh), 0.1);\natk_coeff = exp(-1 / (atk_ms * 0.001 * samplerate));\n\nspd0 = clamp(abs(s0), 0, 1);\nspd1 = clamp(abs(s1), 0, 1);\nspd2 = clamp(abs(s2), 0, 1);\nspd3 = clamp(abs(s3), 0, 1);\nspd4 = clamp(abs(s4), 0, 1);\nspd5 = clamp(abs(s5), 0, 1);\nspd6 = clamp(abs(s6), 0, 1);\nspd7 = clamp(abs(s7), 0, 1);\nspd8 = clamp(abs(s8), 0, 1);\nspd9 = clamp(abs(s9), 0, 1);\nspd10 = clamp(abs(s10), 0, 1);\nspd11 = clamp(abs(s11), 0, 1);\nspd12 = clamp(abs(s12), 0, 1);\nspd13 = clamp(abs(s13), 0, 1);\nspd14 = clamp(abs(s14), 0, 1);\nspd15 = clamp(abs(s15), 0, 1);\n\ndec0 = mix(slow_decay_ms, fast_decay_ms, spd0);\ndec1 = mix(slow_decay_ms, fast_decay_ms, spd1);\ndec2 = mix(slow_decay_ms, fast_decay_ms, spd2);\ndec3 = mix(slow_decay_ms, fast_decay_ms, spd3);\ndec4 = mix(slow_decay_ms, fast_decay_ms, spd4);\ndec5 = mix(slow_decay_ms, fast_decay_ms, spd5);\ndec6 = mix(slow_decay_ms, fast_decay_ms, spd6);\ndec7 = mix(slow_decay_ms, fast_decay_ms, spd7);\ndec8 = mix(slow_decay_ms, fast_decay_ms, spd8);\ndec9 = mix(slow_decay_ms, fast_decay_ms, spd9);\ndec10 = mix(slow_decay_ms, fast_decay_ms, spd10);\ndec11 = mix(slow_decay_ms, fast_decay_ms, spd11);\ndec12 = mix(slow_decay_ms, fast_decay_ms, spd12);\ndec13 = mix(slow_decay_ms, fast_decay_ms, spd13);\ndec14 = mix(slow_decay_ms, fast_decay_ms, spd14);\ndec15 = mix(slow_decay_ms, fast_decay_ms, spd15);\n\ndc0 = exp(-1 / (max(dec0, 0.1) * 0.001 * samplerate));\ndc1 = exp(-1 / (max(dec1, 0.1) * 0.001 * samplerate));\ndc2 = exp(-1 / (max(dec2, 0.1) * 0.001 * samplerate));\ndc3 = exp(-1 / (max(dec3, 0.1) * 0.001 * samplerate));\ndc4 = exp(-1 / (max(dec4, 0.1) * 0.001 * samplerate));\ndc5 = exp(-1 / (max(dec5, 0.1) * 0.001 * samplerate));\ndc6 = exp(-1 / (max(dec6, 0.1) * 0.001 * samplerate));\ndc7 = exp(-1 / (max(dec7, 0.1) * 0.001 * samplerate));\ndc8 = exp(-1 / (max(dec8, 0.1) * 0.001 * samplerate));\ndc9 = exp(-1 / (max(dec9, 0.1) * 0.001 * samplerate));\ndc10 = exp(-1 / (max(dec10, 0.1) * 0.001 * samplerate));\ndc11 = exp(-1 / (max(dec11, 0.1) * 0.001 * samplerate));\ndc12 = exp(-1 / (max(dec12, 0.1) * 0.001 * samplerate));\ndc13 = exp(-1 / (max(dec13, 0.1) * 0.001 * samplerate));\ndc14 = exp(-1 / (max(dec14, 0.1) * 0.001 * samplerate));\ndc15 = exp(-1 / (max(dec15, 0.1) * 0.001 * samplerate));\n\n// Higher entropy lifts weaker modes. Higher purity makes excitation more selective.\nexc_shape = mix(0.55, 1.6, pur);\nt0 = pow(sm0 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt1 = pow(sm1 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt2 = pow(sm2 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt3 = pow(sm3 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt4 = pow(sm4 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt5 = pow(sm5 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt6 = pow(sm6 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt7 = pow(sm7 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt8 = pow(sm8 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt9 = pow(sm9 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt10 = pow(sm10 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt11 = pow(sm11 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt12 = pow(sm12 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt13 = pow(sm13 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt14 = pow(sm14 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt15 = pow(sm15 + 0.00001, exc_shape) * mix(0.35, 1, ent);\n\ne0 = (t0 > e0) * (t0 + atk_coeff * (e0 - t0)) + (t0 <= e0) * (t0 + dc0 * (e0 - t0));\ne1 = (t1 > e1) * (t1 + atk_coeff * (e1 - t1)) + (t1 <= e1) * (t1 + dc1 * (e1 - t1));\ne2 = (t2 > e2) * (t2 + atk_coeff * (e2 - t2)) + (t2 <= e2) * (t2 + dc2 * (e2 - t2));\ne3 = (t3 > e3) * (t3 + atk_coeff * (e3 - t3)) + (t3 <= e3) * (t3 + dc3 * (e3 - t3));\ne4 = (t4 > e4) * (t4 + atk_coeff * (e4 - t4)) + (t4 <= e4) * (t4 + dc4 * (e4 - t4));\ne5 = (t5 > e5) * (t5 + atk_coeff * (e5 - t5)) + (t5 <= e5) * (t5 + dc5 * (e5 - t5));\ne6 = (t6 > e6) * (t6 + atk_coeff * (e6 - t6)) + (t6 <= e6) * (t6 + dc6 * (e6 - t6));\ne7 = (t7 > e7) * (t7 + atk_coeff * (e7 - t7)) + (t7 <= e7) * (t7 + dc7 * (e7 - t7));\ne8 = (t8 > e8) * (t8 + atk_coeff * (e8 - t8)) + (t8 <= e8) * (t8 + dc8 * (e8 - t8));\ne9 = (t9 > e9) * (t9 + atk_coeff * (e9 - t9)) + (t9 <= e9) * (t9 + dc9 * (e9 - t9));\ne10 = (t10 > e10) * (t10 + atk_coeff * (e10 - t10)) + (t10 <= e10) * (t10 + dc10 * (e10 - t10));\ne11 = (t11 > e11) * (t11 + atk_coeff * (e11 - t11)) + (t11 <= e11) * (t11 + dc11 * (e11 - t11));\ne12 = (t12 > e12) * (t12 + atk_coeff * (e12 - t12)) + (t12 <= e12) * (t12 + dc12 * (e12 - t12));\ne13 = (t13 > e13) * (t13 + atk_coeff * (e13 - t13)) + (t13 <= e13) * (t13 + dc13 * (e13 - t13));\ne14 = (t14 > e14) * (t14 + atk_coeff * (e14 - t14)) + (t14 <= e14) * (t14 + dc14 * (e14 - t14));\ne15 = (t15 > e15) * (t15 + atk_coeff * (e15 - t15)) + (t15 <= e15) * (t15 + dc15 * (e15 - t15));\n\nbright = clamp(brightness + ent * 0.18 + (quantum_brightness - 0.5) * 0.55, 0, 1);\n\np0 = fract(p0 + freq * max(h0, 0.01) / samplerate);\np1 = fract(p1 + freq * max(h1, 0.01) / samplerate);\np2 = fract(p2 + freq * max(h2, 0.01) / samplerate);\np3 = fract(p3 + freq * max(h3, 0.01) / samplerate);\np4 = fract(p4 + freq * max(h4, 0.01) / samplerate);\np5 = fract(p5 + freq * max(h5, 0.01) / samplerate);\np6 = fract(p6 + freq * max(h6, 0.01) / samplerate);\np7 = fract(p7 + freq * max(h7, 0.01) / samplerate);\np8 = fract(p8 + freq * max(h8, 0.01) / samplerate);\np9 = fract(p9 + freq * max(h9, 0.01) / samplerate);\np10 = fract(p10 + freq * max(h10, 0.01) / samplerate);\np11 = fract(p11 + freq * max(h11, 0.01) / samplerate);\np12 = fract(p12 + freq * max(h12, 0.01) / samplerate);\np13 = fract(p13 + freq * max(h13, 0.01) / samplerate);\np14 = fract(p14 + freq * max(h14, 0.01) / samplerate);\np15 = fract(p15 + freq * max(h15, 0.01) / samplerate);\n\ntwopi = 6.283185307179586;\npartials =\n    e0 * sin(twopi * p0 + sph0) / pow(max(h0, 1), bright) +\n    e1 * sin(twopi * p1 + sph1) / pow(max(h1, 1), bright) +\n    e2 * sin(twopi * p2 + sph2) / pow(max(h2, 1), bright) +\n    e3 * sin(twopi * p3 + sph3) / pow(max(h3, 1), bright) +\n    e4 * sin(twopi * p4 + sph4) / pow(max(h4, 1), bright) +\n    e5 * sin(twopi * p5 + sph5) / pow(max(h5, 1), bright) +\n    e6 * sin(twopi * p6 + sph6) / pow(max(h6, 1), bright) +\n    e7 * sin(twopi * p7 + sph7) / pow(max(h7, 1), bright) +\n    e8 * sin(twopi * p8 + sph8) / pow(max(h8, 1), bright) +\n    e9 * sin(twopi * p9 + sph9) / pow(max(h9, 1), bright) +\n    e10 * sin(twopi * p10 + sph10) / pow(max(h10, 1), bright) +\n    e11 * sin(twopi * p11 + sph11) / pow(max(h11, 1), bright) +\n    e12 * sin(twopi * p12 + sph12) / pow(max(h12, 1), bright) +\n    e13 * sin(twopi * p13 + sph13) / pow(max(h13, 1), bright) +\n    e14 * sin(twopi * p14 + sph14) / pow(max(h14, 1), bright) +\n    e15 * sin(twopi * p15 + sph15) / pow(max(h15, 1), bright);\n\nraw_modal_noise = noise();\nnoise_color_coeff = exp(-1 / (max(noise_decay_ms, 0.1) * 0.001 * samplerate));\nmodal_noise_lp = raw_modal_noise + noise_color_coeff * (modal_noise_lp - raw_modal_noise);\ncolored_modal_noise = mix(modal_noise_lp, raw_modal_noise, clamp(noise_color, 0, 1));\nquantum_trigger = (quantum_pulse > 0.5) * (quantum_pulse_z <= 0.5);\nquantum_pulse_z = quantum_pulse;\nquantum_decay_coeff = exp(-1 / (max(quantum_event_decay_ms, 1) * 0.001 * samplerate));\nquantum_event_env = quantum_trigger + (1 - quantum_trigger) * quantum_event_env * quantum_decay_coeff;\nnoise_level = (clamp(noise_floor, 0, 0.25) + 0.25 * clamp(noise_amount, 0, 1))\n    * clamp(quantum_noise_variation, 0, 1)\n    * (0.06 + 0.94 * clamp(quantum_event_env, 0, 1));\nnoise_input = colored_modal_noise * noise_level;\nmodal_q_eff = clamp(noise_spectral_q * 4 * mix(0.72, 1.45, pur), 2, 120);\nnf0 = clamp(freq * max(h0, 0.01), max(20, noise_spectral_base_hz * 0.25), samplerate * 0.45);\nng0 = tan(3.141592653589793 * nf0 / samplerate);\nna0 = 1 / (1 + ng0 * (ng0 + 1 / modal_q_eff));\nnv0 = na0 * (nb0 + ng0 * (noise_input - nl0));\nnlv0 = nl0 + ng0 * nv0;\nnb0 = 2 * nv0 - nb0;\nnl0 = 2 * nlv0 - nl0;\nnf1 = clamp(freq * max(h1, 0.01), max(20, noise_spectral_base_hz * 0.25), samplerate * 0.45);\nng1 = tan(3.141592653589793 * nf1 / samplerate);\nna1 = 1 / (1 + ng1 * (ng1 + 1 / modal_q_eff));\nnv1 = na1 * (nb1 + ng1 * (noise_input - nl1));\nnlv1 = nl1 + ng1 * nv1;\nnb1 = 2 * nv1 - nb1;\nnl1 = 2 * nlv1 - nl1;\nnf2 = clamp(freq * max(h2, 0.01), max(20, noise_spectral_base_hz * 0.25), samplerate * 0.45);\nng2 = tan(3.141592653589793 * nf2 / samplerate);\nna2 = 1 / (1 + ng2 * (ng2 + 1 / modal_q_eff));\nnv2 = na2 * (nb2 + ng2 * (noise_input - nl2));\nnlv2 = nl2 + ng2 * nv2;\nnb2 = 2 * nv2 - nb2;\nnl2 = 2 * nlv2 - nl2;\nnf3 = clamp(freq * max(h3, 0.01), max(20, noise_spectral_base_hz * 0.25), samplerate * 0.45);\nng3 = tan(3.141592653589793 * nf3 / samplerate);\nna3 = 1 / (1 + ng3 * (ng3 + 1 / modal_q_eff));\nnv3 = na3 * (nb3 + ng3 * (noise_input - nl3));\nnlv3 = nl3 + ng3 * nv3;\nnb3 = 2 * nv3 - nb3;\nnl3 = 2 * nlv3 - nl3;\nnf4 = clamp(freq * max(h4, 0.01), max(20, noise_spectral_base_hz * 0.25), samplerate * 0.45);\nng4 = tan(3.141592653589793 * nf4 / samplerate);\nna4 = 1 / (1 + ng4 * (ng4 + 1 / modal_q_eff));\nnv4 = na4 * (nb4 + ng4 * (noise_input - nl4));\nnlv4 = nl4 + ng4 * nv4;\nnb4 = 2 * nv4 - nb4;\nnl4 = 2 * nlv4 - nl4;\nnf5 = clamp(freq * max(h5, 0.01), max(20, noise_spectral_base_hz * 0.25), samplerate * 0.45);\nng5 = tan(3.141592653589793 * nf5 / samplerate);\nna5 = 1 / (1 + ng5 * (ng5 + 1 / modal_q_eff));\nnv5 = na5 * (nb5 + ng5 * (noise_input - nl5));\nnlv5 = nl5 + ng5 * nv5;\nnb5 = 2 * nv5 - nb5;\nnl5 = 2 * nlv5 - nl5;\nnf6 = clamp(freq * max(h6, 0.01), max(20, noise_spectral_base_hz * 0.25), samplerate * 0.45);\nng6 = tan(3.141592653589793 * nf6 / samplerate);\nna6 = 1 / (1 + ng6 * (ng6 + 1 / modal_q_eff));\nnv6 = na6 * (nb6 + ng6 * (noise_input - nl6));\nnlv6 = nl6 + ng6 * nv6;\nnb6 = 2 * nv6 - nb6;\nnl6 = 2 * nlv6 - nl6;\nnf7 = clamp(freq * max(h7, 0.01), max(20, noise_spectral_base_hz * 0.25), samplerate * 0.45);\nng7 = tan(3.141592653589793 * nf7 / samplerate);\nna7 = 1 / (1 + ng7 * (ng7 + 1 / modal_q_eff));\nnv7 = na7 * (nb7 + ng7 * (noise_input - nl7));\nnlv7 = nl7 + ng7 * nv7;\nnb7 = 2 * nv7 - nb7;\nnl7 = 2 * nlv7 - nl7;\nnf8 = clamp(freq * max(h8, 0.01), max(20, noise_spectral_base_hz * 0.25), samplerate * 0.45);\nng8 = tan(3.141592653589793 * nf8 / samplerate);\nna8 = 1 / (1 + ng8 * (ng8 + 1 / modal_q_eff));\nnv8 = na8 * (nb8 + ng8 * (noise_input - nl8));\nnlv8 = nl8 + ng8 * nv8;\nnb8 = 2 * nv8 - nb8;\nnl8 = 2 * nlv8 - nl8;\nnf9 = clamp(freq * max(h9, 0.01), max(20, noise_spectral_base_hz * 0.25), samplerate * 0.45);\nng9 = tan(3.141592653589793 * nf9 / samplerate);\nna9 = 1 / (1 + ng9 * (ng9 + 1 / modal_q_eff));\nnv9 = na9 * (nb9 + ng9 * (noise_input - nl9));\nnlv9 = nl9 + ng9 * nv9;\nnb9 = 2 * nv9 - nb9;\nnl9 = 2 * nlv9 - nl9;\nnf10 = clamp(freq * max(h10, 0.01), max(20, noise_spectral_base_hz * 0.25), samplerate * 0.45);\nng10 = tan(3.141592653589793 * nf10 / samplerate);\nna10 = 1 / (1 + ng10 * (ng10 + 1 / modal_q_eff));\nnv10 = na10 * (nb10 + ng10 * (noise_input - nl10));\nnlv10 = nl10 + ng10 * nv10;\nnb10 = 2 * nv10 - nb10;\nnl10 = 2 * nlv10 - nl10;\nnf11 = clamp(freq * max(h11, 0.01), max(20, noise_spectral_base_hz * 0.25), samplerate * 0.45);\nng11 = tan(3.141592653589793 * nf11 / samplerate);\nna11 = 1 / (1 + ng11 * (ng11 + 1 / modal_q_eff));\nnv11 = na11 * (nb11 + ng11 * (noise_input - nl11));\nnlv11 = nl11 + ng11 * nv11;\nnb11 = 2 * nv11 - nb11;\nnl11 = 2 * nlv11 - nl11;\nnf12 = clamp(freq * max(h12, 0.01), max(20, noise_spectral_base_hz * 0.25), samplerate * 0.45);\nng12 = tan(3.141592653589793 * nf12 / samplerate);\nna12 = 1 / (1 + ng12 * (ng12 + 1 / modal_q_eff));\nnv12 = na12 * (nb12 + ng12 * (noise_input - nl12));\nnlv12 = nl12 + ng12 * nv12;\nnb12 = 2 * nv12 - nb12;\nnl12 = 2 * nlv12 - nl12;\nnf13 = clamp(freq * max(h13, 0.01), max(20, noise_spectral_base_hz * 0.25), samplerate * 0.45);\nng13 = tan(3.141592653589793 * nf13 / samplerate);\nna13 = 1 / (1 + ng13 * (ng13 + 1 / modal_q_eff));\nnv13 = na13 * (nb13 + ng13 * (noise_input - nl13));\nnlv13 = nl13 + ng13 * nv13;\nnb13 = 2 * nv13 - nb13;\nnl13 = 2 * nlv13 - nl13;\nnf14 = clamp(freq * max(h14, 0.01), max(20, noise_spectral_base_hz * 0.25), samplerate * 0.45);\nng14 = tan(3.141592653589793 * nf14 / samplerate);\nna14 = 1 / (1 + ng14 * (ng14 + 1 / modal_q_eff));\nnv14 = na14 * (nb14 + ng14 * (noise_input - nl14));\nnlv14 = nl14 + ng14 * nv14;\nnb14 = 2 * nv14 - nb14;\nnl14 = 2 * nlv14 - nl14;\nnf15 = clamp(freq * max(h15, 0.01), max(20, noise_spectral_base_hz * 0.25), samplerate * 0.45);\nng15 = tan(3.141592653589793 * nf15 / samplerate);\nna15 = 1 / (1 + ng15 * (ng15 + 1 / modal_q_eff));\nnv15 = na15 * (nb15 + ng15 * (noise_input - nl15));\nnlv15 = nl15 + ng15 * nv15;\nnb15 = 2 * nv15 - nb15;\nnl15 = 2 * nlv15 - nl15;\nmodal_noise = (\n    e0 * nv0 +\n    e1 * nv1 +\n    e2 * nv2 +\n    e3 * nv3 +\n    e4 * nv4 +\n    e5 * nv5 +\n    e6 * nv6 +\n    e7 * nv7 +\n    e8 * nv8 +\n    e9 * nv9 +\n    e10 * nv10 +\n    e11 * nv11 +\n    e12 * nv12 +\n    e13 * nv13 +\n    e14 * nv14 +\n    e15 * nv15\n) / sqrt(16);\nmodal_noise = tanh(modal_noise * clamp(noise_spectral_gain, 0, 8));\nmodal_noise = mix(colored_modal_noise * noise_level, modal_noise, clamp(noise_spectral_amount, 0, 1));\n\nvoice_scale = 1 / sqrt(max(mix_voices, 1));\nsig = mix(partials, modal_noise, clamp(noise_resonator_mix, 0, 1));\n\nout1 = sig * amp * output_ceiling * voice_scale;\nout2 = e0 + e1 + e2 + e3 + e4 + e5 + e6 + e7 + e8 + e9 + e10 + e11 + e12 + e13 + e14 + e15;\nout3 = freq;\n",
                    "fontface": 0,
                    "fontname": "<Monospaced>",
                    "fontsize": 12.0,
                    "id": "obj-63",
                    "maxclass": "gen.codebox~",
                    "numinlets": 1,
                    "numoutlets": 3,
                    "outlettype": [
                        "signal",
                        "signal",
                        "signal"
                    ],
                    "patching_rect": [
                        416.0,
                        386.5,
                        165.0,
                        32.0
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-64",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [
                        "signal"
                    ],
                    "patching_rect": [
                        440.0,
                        315.0,
                        31.0,
                        22.0
                    ],
                    "text": "sig~"
                }
            },
            {
                "box": {
                    "format": 6,
                    "id": "obj-65",
                    "maxclass": "flonum",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        "bang"
                    ],
                    "parameter_enable": 0,
                    "patching_rect": [
                        439.0,
                        271.0,
                        50.0,
                        22.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        161.0,
                        118.0,
                        50.0,
                        22.0
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-21",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        265.0,
                        337.0,
                        79.0,
                        22.0
                    ],
                    "text": "prepend amp"
                }
            },
            {
                "box": {
                    "format": 6,
                    "id": "obj-22",
                    "maxclass": "flonum",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        "bang"
                    ],
                    "parameter_enable": 0,
                    "patching_rect": [
                        295.0,
                        299.0,
                        50.0,
                        22.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        102.0,
                        148.0,
                        50.0,
                        22.0
                    ]
                }
            },
            {
                "box": {
                    "code": "// QMW Density Field Quantum Resonator 16\n//\n// Gen~ codebox.\n// in1 is the carrier frequency in Hz.\n// m0..m15 excite sixteen resonant partials.\n// ph0..ph15 set smoothed per-partial timing/phase.\n// s0..s15 set lifetime: fast lanes flash, slow lanes ring.\n// h0..h15 are partial ratios. Defaults are harmonic 1..16, but these can\n// later be replaced by Hamiltonian energy-gap ratios.\n\nParam m0(0);\nParam m1(0);\nParam m2(0);\nParam m3(0);\nParam m4(0);\nParam m5(0);\nParam m6(0);\nParam m7(0);\nParam m8(0);\nParam m9(0);\nParam m10(0);\nParam m11(0);\nParam m12(0);\nParam m13(0);\nParam m14(0);\nParam m15(0);\n\nParam ph0(0);\nParam ph1(0);\nParam ph2(0);\nParam ph3(0);\nParam ph4(0);\nParam ph5(0);\nParam ph6(0);\nParam ph7(0);\nParam ph8(0);\nParam ph9(0);\nParam ph10(0);\nParam ph11(0);\nParam ph12(0);\nParam ph13(0);\nParam ph14(0);\nParam ph15(0);\n\nParam s0(0);\nParam s1(0);\nParam s2(0);\nParam s3(0);\nParam s4(0);\nParam s5(0);\nParam s6(0);\nParam s7(0);\nParam s8(0);\nParam s9(0);\nParam s10(0);\nParam s11(0);\nParam s12(0);\nParam s13(0);\nParam s14(0);\nParam s15(0);\n\nParam h0(1);\nParam h1(2);\nParam h2(3);\nParam h3(4);\nParam h4(5);\nParam h5(6);\nParam h6(7);\nParam h7(8);\nParam h8(9);\nParam h9(10);\nParam h10(11);\nParam h11(12);\nParam h12(13);\nParam h13(14);\nParam h14(15);\nParam h15(16);\n\nParam purity(1);\nParam entropy(0);\nParam coherence(0);\nParam amp(0.2);\nParam default_freq(55);\nParam attack_ms(350);\nParam slow_decay_ms(3500);\nParam fast_decay_ms(900);\nParam phase_smooth_ms(4000);\nParam magnitude_smooth_ms(2500);\nParam brightness(0.65);\nParam mix_voices(4);\nParam output_ceiling(0.85);\nParam noise_resonator_mix(0.45);\nParam noise_amount(0.28);\nParam noise_floor(0);\nParam noise_color(0.72);\nParam noise_decay_ms(45);\nParam noise_spectral_amount(0.75);\nParam noise_spectral_gain(2.5);\nParam noise_spectral_base_hz(55);\nParam noise_spectral_q(7);\nParam quantum_pulse(0);\nParam quantum_noise_variation(0.25);\nParam quantum_brightness(0.5);\nParam quantum_event_decay_ms(1200);\nHistory quantum_pulse_z(0);\nHistory quantum_event_env(0);\nHistory modal_noise_lp(0);\nHistory nb0(0); History nl0(0);\nHistory nb1(0); History nl1(0);\nHistory nb2(0); History nl2(0);\nHistory nb3(0); History nl3(0);\nHistory nb4(0); History nl4(0);\nHistory nb5(0); History nl5(0);\nHistory nb6(0); History nl6(0);\nHistory nb7(0); History nl7(0);\nHistory nb8(0); History nl8(0);\nHistory nb9(0); History nl9(0);\nHistory nb10(0); History nl10(0);\nHistory nb11(0); History nl11(0);\nHistory nb12(0); History nl12(0);\nHistory nb13(0); History nl13(0);\nHistory nb14(0); History nl14(0);\nHistory nb15(0); History nl15(0);\n\nHistory p0(0);\nHistory p1(0);\nHistory p2(0);\nHistory p3(0);\nHistory p4(0);\nHistory p5(0);\nHistory p6(0);\nHistory p7(0);\nHistory p8(0);\nHistory p9(0);\nHistory p10(0);\nHistory p11(0);\nHistory p12(0);\nHistory p13(0);\nHistory p14(0);\nHistory p15(0);\n\nHistory e0(0);\nHistory e1(0);\nHistory e2(0);\nHistory e3(0);\nHistory e4(0);\nHistory e5(0);\nHistory e6(0);\nHistory e7(0);\nHistory e8(0);\nHistory e9(0);\nHistory e10(0);\nHistory e11(0);\nHistory e12(0);\nHistory e13(0);\nHistory e14(0);\nHistory e15(0);\n\nHistory sm0(0);\nHistory sm1(0);\nHistory sm2(0);\nHistory sm3(0);\nHistory sm4(0);\nHistory sm5(0);\nHistory sm6(0);\nHistory sm7(0);\nHistory sm8(0);\nHistory sm9(0);\nHistory sm10(0);\nHistory sm11(0);\nHistory sm12(0);\nHistory sm13(0);\nHistory sm14(0);\nHistory sm15(0);\n\nHistory sph0(0);\nHistory sph1(0);\nHistory sph2(0);\nHistory sph3(0);\nHistory sph4(0);\nHistory sph5(0);\nHistory sph6(0);\nHistory sph7(0);\nHistory sph8(0);\nHistory sph9(0);\nHistory sph10(0);\nHistory sph11(0);\nHistory sph12(0);\nHistory sph13(0);\nHistory sph14(0);\nHistory sph15(0);\n\nfreq = (in1 > 0) * in1 + (in1 <= 0) * default_freq;\npur = clamp(purity, 0, 1);\nent = clamp(entropy, 0, 1);\ncoh = clamp(coherence, 0, 1);\n\nmag_ms = max(magnitude_smooth_ms, 0.1);\nmag_coeff = exp(-1 / (mag_ms * 0.001 * samplerate));\n\ntm0 = clamp(m0, 0, 1);\ntm1 = clamp(m1, 0, 1);\ntm2 = clamp(m2, 0, 1);\ntm3 = clamp(m3, 0, 1);\ntm4 = clamp(m4, 0, 1);\ntm5 = clamp(m5, 0, 1);\ntm6 = clamp(m6, 0, 1);\ntm7 = clamp(m7, 0, 1);\ntm8 = clamp(m8, 0, 1);\ntm9 = clamp(m9, 0, 1);\ntm10 = clamp(m10, 0, 1);\ntm11 = clamp(m11, 0, 1);\ntm12 = clamp(m12, 0, 1);\ntm13 = clamp(m13, 0, 1);\ntm14 = clamp(m14, 0, 1);\ntm15 = clamp(m15, 0, 1);\n\nsm0 = tm0 + mag_coeff * (sm0 - tm0);\nsm1 = tm1 + mag_coeff * (sm1 - tm1);\nsm2 = tm2 + mag_coeff * (sm2 - tm2);\nsm3 = tm3 + mag_coeff * (sm3 - tm3);\nsm4 = tm4 + mag_coeff * (sm4 - tm4);\nsm5 = tm5 + mag_coeff * (sm5 - tm5);\nsm6 = tm6 + mag_coeff * (sm6 - tm6);\nsm7 = tm7 + mag_coeff * (sm7 - tm7);\nsm8 = tm8 + mag_coeff * (sm8 - tm8);\nsm9 = tm9 + mag_coeff * (sm9 - tm9);\nsm10 = tm10 + mag_coeff * (sm10 - tm10);\nsm11 = tm11 + mag_coeff * (sm11 - tm11);\nsm12 = tm12 + mag_coeff * (sm12 - tm12);\nsm13 = tm13 + mag_coeff * (sm13 - tm13);\nsm14 = tm14 + mag_coeff * (sm14 - tm14);\nsm15 = tm15 + mag_coeff * (sm15 - tm15);\n\nphase_ms = max(phase_smooth_ms, 0.1);\nphase_coeff = exp(-1 / (phase_ms * 0.001 * samplerate));\n\ndph0 = atan2(sin(ph0 - sph0), cos(ph0 - sph0));\ndph1 = atan2(sin(ph1 - sph1), cos(ph1 - sph1));\ndph2 = atan2(sin(ph2 - sph2), cos(ph2 - sph2));\ndph3 = atan2(sin(ph3 - sph3), cos(ph3 - sph3));\ndph4 = atan2(sin(ph4 - sph4), cos(ph4 - sph4));\ndph5 = atan2(sin(ph5 - sph5), cos(ph5 - sph5));\ndph6 = atan2(sin(ph6 - sph6), cos(ph6 - sph6));\ndph7 = atan2(sin(ph7 - sph7), cos(ph7 - sph7));\ndph8 = atan2(sin(ph8 - sph8), cos(ph8 - sph8));\ndph9 = atan2(sin(ph9 - sph9), cos(ph9 - sph9));\ndph10 = atan2(sin(ph10 - sph10), cos(ph10 - sph10));\ndph11 = atan2(sin(ph11 - sph11), cos(ph11 - sph11));\ndph12 = atan2(sin(ph12 - sph12), cos(ph12 - sph12));\ndph13 = atan2(sin(ph13 - sph13), cos(ph13 - sph13));\ndph14 = atan2(sin(ph14 - sph14), cos(ph14 - sph14));\ndph15 = atan2(sin(ph15 - sph15), cos(ph15 - sph15));\n\nsph0 = sph0 + (1 - phase_coeff) * dph0;\nsph1 = sph1 + (1 - phase_coeff) * dph1;\nsph2 = sph2 + (1 - phase_coeff) * dph2;\nsph3 = sph3 + (1 - phase_coeff) * dph3;\nsph4 = sph4 + (1 - phase_coeff) * dph4;\nsph5 = sph5 + (1 - phase_coeff) * dph5;\nsph6 = sph6 + (1 - phase_coeff) * dph6;\nsph7 = sph7 + (1 - phase_coeff) * dph7;\nsph8 = sph8 + (1 - phase_coeff) * dph8;\nsph9 = sph9 + (1 - phase_coeff) * dph9;\nsph10 = sph10 + (1 - phase_coeff) * dph10;\nsph11 = sph11 + (1 - phase_coeff) * dph11;\nsph12 = sph12 + (1 - phase_coeff) * dph12;\nsph13 = sph13 + (1 - phase_coeff) * dph13;\nsph14 = sph14 + (1 - phase_coeff) * dph14;\nsph15 = sph15 + (1 - phase_coeff) * dph15;\n\natk_ms = max(attack_ms * mix(1.35, 0.65, coh), 0.1);\natk_coeff = exp(-1 / (atk_ms * 0.001 * samplerate));\n\nspd0 = clamp(abs(s0), 0, 1);\nspd1 = clamp(abs(s1), 0, 1);\nspd2 = clamp(abs(s2), 0, 1);\nspd3 = clamp(abs(s3), 0, 1);\nspd4 = clamp(abs(s4), 0, 1);\nspd5 = clamp(abs(s5), 0, 1);\nspd6 = clamp(abs(s6), 0, 1);\nspd7 = clamp(abs(s7), 0, 1);\nspd8 = clamp(abs(s8), 0, 1);\nspd9 = clamp(abs(s9), 0, 1);\nspd10 = clamp(abs(s10), 0, 1);\nspd11 = clamp(abs(s11), 0, 1);\nspd12 = clamp(abs(s12), 0, 1);\nspd13 = clamp(abs(s13), 0, 1);\nspd14 = clamp(abs(s14), 0, 1);\nspd15 = clamp(abs(s15), 0, 1);\n\ndec0 = mix(slow_decay_ms, fast_decay_ms, spd0);\ndec1 = mix(slow_decay_ms, fast_decay_ms, spd1);\ndec2 = mix(slow_decay_ms, fast_decay_ms, spd2);\ndec3 = mix(slow_decay_ms, fast_decay_ms, spd3);\ndec4 = mix(slow_decay_ms, fast_decay_ms, spd4);\ndec5 = mix(slow_decay_ms, fast_decay_ms, spd5);\ndec6 = mix(slow_decay_ms, fast_decay_ms, spd6);\ndec7 = mix(slow_decay_ms, fast_decay_ms, spd7);\ndec8 = mix(slow_decay_ms, fast_decay_ms, spd8);\ndec9 = mix(slow_decay_ms, fast_decay_ms, spd9);\ndec10 = mix(slow_decay_ms, fast_decay_ms, spd10);\ndec11 = mix(slow_decay_ms, fast_decay_ms, spd11);\ndec12 = mix(slow_decay_ms, fast_decay_ms, spd12);\ndec13 = mix(slow_decay_ms, fast_decay_ms, spd13);\ndec14 = mix(slow_decay_ms, fast_decay_ms, spd14);\ndec15 = mix(slow_decay_ms, fast_decay_ms, spd15);\n\ndc0 = exp(-1 / (max(dec0, 0.1) * 0.001 * samplerate));\ndc1 = exp(-1 / (max(dec1, 0.1) * 0.001 * samplerate));\ndc2 = exp(-1 / (max(dec2, 0.1) * 0.001 * samplerate));\ndc3 = exp(-1 / (max(dec3, 0.1) * 0.001 * samplerate));\ndc4 = exp(-1 / (max(dec4, 0.1) * 0.001 * samplerate));\ndc5 = exp(-1 / (max(dec5, 0.1) * 0.001 * samplerate));\ndc6 = exp(-1 / (max(dec6, 0.1) * 0.001 * samplerate));\ndc7 = exp(-1 / (max(dec7, 0.1) * 0.001 * samplerate));\ndc8 = exp(-1 / (max(dec8, 0.1) * 0.001 * samplerate));\ndc9 = exp(-1 / (max(dec9, 0.1) * 0.001 * samplerate));\ndc10 = exp(-1 / (max(dec10, 0.1) * 0.001 * samplerate));\ndc11 = exp(-1 / (max(dec11, 0.1) * 0.001 * samplerate));\ndc12 = exp(-1 / (max(dec12, 0.1) * 0.001 * samplerate));\ndc13 = exp(-1 / (max(dec13, 0.1) * 0.001 * samplerate));\ndc14 = exp(-1 / (max(dec14, 0.1) * 0.001 * samplerate));\ndc15 = exp(-1 / (max(dec15, 0.1) * 0.001 * samplerate));\n\n// Higher entropy lifts weaker modes. Higher purity makes excitation more selective.\nexc_shape = mix(0.55, 1.6, pur);\nt0 = pow(sm0 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt1 = pow(sm1 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt2 = pow(sm2 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt3 = pow(sm3 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt4 = pow(sm4 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt5 = pow(sm5 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt6 = pow(sm6 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt7 = pow(sm7 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt8 = pow(sm8 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt9 = pow(sm9 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt10 = pow(sm10 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt11 = pow(sm11 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt12 = pow(sm12 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt13 = pow(sm13 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt14 = pow(sm14 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt15 = pow(sm15 + 0.00001, exc_shape) * mix(0.35, 1, ent);\n\ne0 = (t0 > e0) * (t0 + atk_coeff * (e0 - t0)) + (t0 <= e0) * (t0 + dc0 * (e0 - t0));\ne1 = (t1 > e1) * (t1 + atk_coeff * (e1 - t1)) + (t1 <= e1) * (t1 + dc1 * (e1 - t1));\ne2 = (t2 > e2) * (t2 + atk_coeff * (e2 - t2)) + (t2 <= e2) * (t2 + dc2 * (e2 - t2));\ne3 = (t3 > e3) * (t3 + atk_coeff * (e3 - t3)) + (t3 <= e3) * (t3 + dc3 * (e3 - t3));\ne4 = (t4 > e4) * (t4 + atk_coeff * (e4 - t4)) + (t4 <= e4) * (t4 + dc4 * (e4 - t4));\ne5 = (t5 > e5) * (t5 + atk_coeff * (e5 - t5)) + (t5 <= e5) * (t5 + dc5 * (e5 - t5));\ne6 = (t6 > e6) * (t6 + atk_coeff * (e6 - t6)) + (t6 <= e6) * (t6 + dc6 * (e6 - t6));\ne7 = (t7 > e7) * (t7 + atk_coeff * (e7 - t7)) + (t7 <= e7) * (t7 + dc7 * (e7 - t7));\ne8 = (t8 > e8) * (t8 + atk_coeff * (e8 - t8)) + (t8 <= e8) * (t8 + dc8 * (e8 - t8));\ne9 = (t9 > e9) * (t9 + atk_coeff * (e9 - t9)) + (t9 <= e9) * (t9 + dc9 * (e9 - t9));\ne10 = (t10 > e10) * (t10 + atk_coeff * (e10 - t10)) + (t10 <= e10) * (t10 + dc10 * (e10 - t10));\ne11 = (t11 > e11) * (t11 + atk_coeff * (e11 - t11)) + (t11 <= e11) * (t11 + dc11 * (e11 - t11));\ne12 = (t12 > e12) * (t12 + atk_coeff * (e12 - t12)) + (t12 <= e12) * (t12 + dc12 * (e12 - t12));\ne13 = (t13 > e13) * (t13 + atk_coeff * (e13 - t13)) + (t13 <= e13) * (t13 + dc13 * (e13 - t13));\ne14 = (t14 > e14) * (t14 + atk_coeff * (e14 - t14)) + (t14 <= e14) * (t14 + dc14 * (e14 - t14));\ne15 = (t15 > e15) * (t15 + atk_coeff * (e15 - t15)) + (t15 <= e15) * (t15 + dc15 * (e15 - t15));\n\nbright = clamp(brightness + ent * 0.18 + (quantum_brightness - 0.5) * 0.55, 0, 1);\n\np0 = fract(p0 + freq * max(h0, 0.01) / samplerate);\np1 = fract(p1 + freq * max(h1, 0.01) / samplerate);\np2 = fract(p2 + freq * max(h2, 0.01) / samplerate);\np3 = fract(p3 + freq * max(h3, 0.01) / samplerate);\np4 = fract(p4 + freq * max(h4, 0.01) / samplerate);\np5 = fract(p5 + freq * max(h5, 0.01) / samplerate);\np6 = fract(p6 + freq * max(h6, 0.01) / samplerate);\np7 = fract(p7 + freq * max(h7, 0.01) / samplerate);\np8 = fract(p8 + freq * max(h8, 0.01) / samplerate);\np9 = fract(p9 + freq * max(h9, 0.01) / samplerate);\np10 = fract(p10 + freq * max(h10, 0.01) / samplerate);\np11 = fract(p11 + freq * max(h11, 0.01) / samplerate);\np12 = fract(p12 + freq * max(h12, 0.01) / samplerate);\np13 = fract(p13 + freq * max(h13, 0.01) / samplerate);\np14 = fract(p14 + freq * max(h14, 0.01) / samplerate);\np15 = fract(p15 + freq * max(h15, 0.01) / samplerate);\n\ntwopi = 6.283185307179586;\npartials =\n    e0 * sin(twopi * p0 + sph0) / pow(max(h0, 1), bright) +\n    e1 * sin(twopi * p1 + sph1) / pow(max(h1, 1), bright) +\n    e2 * sin(twopi * p2 + sph2) / pow(max(h2, 1), bright) +\n    e3 * sin(twopi * p3 + sph3) / pow(max(h3, 1), bright) +\n    e4 * sin(twopi * p4 + sph4) / pow(max(h4, 1), bright) +\n    e5 * sin(twopi * p5 + sph5) / pow(max(h5, 1), bright) +\n    e6 * sin(twopi * p6 + sph6) / pow(max(h6, 1), bright) +\n    e7 * sin(twopi * p7 + sph7) / pow(max(h7, 1), bright) +\n    e8 * sin(twopi * p8 + sph8) / pow(max(h8, 1), bright) +\n    e9 * sin(twopi * p9 + sph9) / pow(max(h9, 1), bright) +\n    e10 * sin(twopi * p10 + sph10) / pow(max(h10, 1), bright) +\n    e11 * sin(twopi * p11 + sph11) / pow(max(h11, 1), bright) +\n    e12 * sin(twopi * p12 + sph12) / pow(max(h12, 1), bright) +\n    e13 * sin(twopi * p13 + sph13) / pow(max(h13, 1), bright) +\n    e14 * sin(twopi * p14 + sph14) / pow(max(h14, 1), bright) +\n    e15 * sin(twopi * p15 + sph15) / pow(max(h15, 1), bright);\n\nraw_modal_noise = noise();\nnoise_color_coeff = exp(-1 / (max(noise_decay_ms, 0.1) * 0.001 * samplerate));\nmodal_noise_lp = raw_modal_noise + noise_color_coeff * (modal_noise_lp - raw_modal_noise);\ncolored_modal_noise = mix(modal_noise_lp, raw_modal_noise, clamp(noise_color, 0, 1));\nquantum_trigger = (quantum_pulse > 0.5) * (quantum_pulse_z <= 0.5);\nquantum_pulse_z = quantum_pulse;\nquantum_decay_coeff = exp(-1 / (max(quantum_event_decay_ms, 1) * 0.001 * samplerate));\nquantum_event_env = quantum_trigger + (1 - quantum_trigger) * quantum_event_env * quantum_decay_coeff;\nnoise_level = (clamp(noise_floor, 0, 0.25) + 0.25 * clamp(noise_amount, 0, 1))\n    * clamp(quantum_noise_variation, 0, 1)\n    * (0.06 + 0.94 * clamp(quantum_event_env, 0, 1));\nnoise_input = colored_modal_noise * noise_level;\nmodal_q_eff = clamp(noise_spectral_q * 4 * mix(0.72, 1.45, pur), 2, 120);\nnf0 = clamp(freq * max(h0, 0.01), max(20, noise_spectral_base_hz * 0.25), samplerate * 0.45);\nng0 = tan(3.141592653589793 * nf0 / samplerate);\nna0 = 1 / (1 + ng0 * (ng0 + 1 / modal_q_eff));\nnv0 = na0 * (nb0 + ng0 * (noise_input - nl0));\nnlv0 = nl0 + ng0 * nv0;\nnb0 = 2 * nv0 - nb0;\nnl0 = 2 * nlv0 - nl0;\nnf1 = clamp(freq * max(h1, 0.01), max(20, noise_spectral_base_hz * 0.25), samplerate * 0.45);\nng1 = tan(3.141592653589793 * nf1 / samplerate);\nna1 = 1 / (1 + ng1 * (ng1 + 1 / modal_q_eff));\nnv1 = na1 * (nb1 + ng1 * (noise_input - nl1));\nnlv1 = nl1 + ng1 * nv1;\nnb1 = 2 * nv1 - nb1;\nnl1 = 2 * nlv1 - nl1;\nnf2 = clamp(freq * max(h2, 0.01), max(20, noise_spectral_base_hz * 0.25), samplerate * 0.45);\nng2 = tan(3.141592653589793 * nf2 / samplerate);\nna2 = 1 / (1 + ng2 * (ng2 + 1 / modal_q_eff));\nnv2 = na2 * (nb2 + ng2 * (noise_input - nl2));\nnlv2 = nl2 + ng2 * nv2;\nnb2 = 2 * nv2 - nb2;\nnl2 = 2 * nlv2 - nl2;\nnf3 = clamp(freq * max(h3, 0.01), max(20, noise_spectral_base_hz * 0.25), samplerate * 0.45);\nng3 = tan(3.141592653589793 * nf3 / samplerate);\nna3 = 1 / (1 + ng3 * (ng3 + 1 / modal_q_eff));\nnv3 = na3 * (nb3 + ng3 * (noise_input - nl3));\nnlv3 = nl3 + ng3 * nv3;\nnb3 = 2 * nv3 - nb3;\nnl3 = 2 * nlv3 - nl3;\nnf4 = clamp(freq * max(h4, 0.01), max(20, noise_spectral_base_hz * 0.25), samplerate * 0.45);\nng4 = tan(3.141592653589793 * nf4 / samplerate);\nna4 = 1 / (1 + ng4 * (ng4 + 1 / modal_q_eff));\nnv4 = na4 * (nb4 + ng4 * (noise_input - nl4));\nnlv4 = nl4 + ng4 * nv4;\nnb4 = 2 * nv4 - nb4;\nnl4 = 2 * nlv4 - nl4;\nnf5 = clamp(freq * max(h5, 0.01), max(20, noise_spectral_base_hz * 0.25), samplerate * 0.45);\nng5 = tan(3.141592653589793 * nf5 / samplerate);\nna5 = 1 / (1 + ng5 * (ng5 + 1 / modal_q_eff));\nnv5 = na5 * (nb5 + ng5 * (noise_input - nl5));\nnlv5 = nl5 + ng5 * nv5;\nnb5 = 2 * nv5 - nb5;\nnl5 = 2 * nlv5 - nl5;\nnf6 = clamp(freq * max(h6, 0.01), max(20, noise_spectral_base_hz * 0.25), samplerate * 0.45);\nng6 = tan(3.141592653589793 * nf6 / samplerate);\nna6 = 1 / (1 + ng6 * (ng6 + 1 / modal_q_eff));\nnv6 = na6 * (nb6 + ng6 * (noise_input - nl6));\nnlv6 = nl6 + ng6 * nv6;\nnb6 = 2 * nv6 - nb6;\nnl6 = 2 * nlv6 - nl6;\nnf7 = clamp(freq * max(h7, 0.01), max(20, noise_spectral_base_hz * 0.25), samplerate * 0.45);\nng7 = tan(3.141592653589793 * nf7 / samplerate);\nna7 = 1 / (1 + ng7 * (ng7 + 1 / modal_q_eff));\nnv7 = na7 * (nb7 + ng7 * (noise_input - nl7));\nnlv7 = nl7 + ng7 * nv7;\nnb7 = 2 * nv7 - nb7;\nnl7 = 2 * nlv7 - nl7;\nnf8 = clamp(freq * max(h8, 0.01), max(20, noise_spectral_base_hz * 0.25), samplerate * 0.45);\nng8 = tan(3.141592653589793 * nf8 / samplerate);\nna8 = 1 / (1 + ng8 * (ng8 + 1 / modal_q_eff));\nnv8 = na8 * (nb8 + ng8 * (noise_input - nl8));\nnlv8 = nl8 + ng8 * nv8;\nnb8 = 2 * nv8 - nb8;\nnl8 = 2 * nlv8 - nl8;\nnf9 = clamp(freq * max(h9, 0.01), max(20, noise_spectral_base_hz * 0.25), samplerate * 0.45);\nng9 = tan(3.141592653589793 * nf9 / samplerate);\nna9 = 1 / (1 + ng9 * (ng9 + 1 / modal_q_eff));\nnv9 = na9 * (nb9 + ng9 * (noise_input - nl9));\nnlv9 = nl9 + ng9 * nv9;\nnb9 = 2 * nv9 - nb9;\nnl9 = 2 * nlv9 - nl9;\nnf10 = clamp(freq * max(h10, 0.01), max(20, noise_spectral_base_hz * 0.25), samplerate * 0.45);\nng10 = tan(3.141592653589793 * nf10 / samplerate);\nna10 = 1 / (1 + ng10 * (ng10 + 1 / modal_q_eff));\nnv10 = na10 * (nb10 + ng10 * (noise_input - nl10));\nnlv10 = nl10 + ng10 * nv10;\nnb10 = 2 * nv10 - nb10;\nnl10 = 2 * nlv10 - nl10;\nnf11 = clamp(freq * max(h11, 0.01), max(20, noise_spectral_base_hz * 0.25), samplerate * 0.45);\nng11 = tan(3.141592653589793 * nf11 / samplerate);\nna11 = 1 / (1 + ng11 * (ng11 + 1 / modal_q_eff));\nnv11 = na11 * (nb11 + ng11 * (noise_input - nl11));\nnlv11 = nl11 + ng11 * nv11;\nnb11 = 2 * nv11 - nb11;\nnl11 = 2 * nlv11 - nl11;\nnf12 = clamp(freq * max(h12, 0.01), max(20, noise_spectral_base_hz * 0.25), samplerate * 0.45);\nng12 = tan(3.141592653589793 * nf12 / samplerate);\nna12 = 1 / (1 + ng12 * (ng12 + 1 / modal_q_eff));\nnv12 = na12 * (nb12 + ng12 * (noise_input - nl12));\nnlv12 = nl12 + ng12 * nv12;\nnb12 = 2 * nv12 - nb12;\nnl12 = 2 * nlv12 - nl12;\nnf13 = clamp(freq * max(h13, 0.01), max(20, noise_spectral_base_hz * 0.25), samplerate * 0.45);\nng13 = tan(3.141592653589793 * nf13 / samplerate);\nna13 = 1 / (1 + ng13 * (ng13 + 1 / modal_q_eff));\nnv13 = na13 * (nb13 + ng13 * (noise_input - nl13));\nnlv13 = nl13 + ng13 * nv13;\nnb13 = 2 * nv13 - nb13;\nnl13 = 2 * nlv13 - nl13;\nnf14 = clamp(freq * max(h14, 0.01), max(20, noise_spectral_base_hz * 0.25), samplerate * 0.45);\nng14 = tan(3.141592653589793 * nf14 / samplerate);\nna14 = 1 / (1 + ng14 * (ng14 + 1 / modal_q_eff));\nnv14 = na14 * (nb14 + ng14 * (noise_input - nl14));\nnlv14 = nl14 + ng14 * nv14;\nnb14 = 2 * nv14 - nb14;\nnl14 = 2 * nlv14 - nl14;\nnf15 = clamp(freq * max(h15, 0.01), max(20, noise_spectral_base_hz * 0.25), samplerate * 0.45);\nng15 = tan(3.141592653589793 * nf15 / samplerate);\nna15 = 1 / (1 + ng15 * (ng15 + 1 / modal_q_eff));\nnv15 = na15 * (nb15 + ng15 * (noise_input - nl15));\nnlv15 = nl15 + ng15 * nv15;\nnb15 = 2 * nv15 - nb15;\nnl15 = 2 * nlv15 - nl15;\nmodal_noise = (\n    e0 * nv0 +\n    e1 * nv1 +\n    e2 * nv2 +\n    e3 * nv3 +\n    e4 * nv4 +\n    e5 * nv5 +\n    e6 * nv6 +\n    e7 * nv7 +\n    e8 * nv8 +\n    e9 * nv9 +\n    e10 * nv10 +\n    e11 * nv11 +\n    e12 * nv12 +\n    e13 * nv13 +\n    e14 * nv14 +\n    e15 * nv15\n) / sqrt(16);\nmodal_noise = tanh(modal_noise * clamp(noise_spectral_gain, 0, 8));\nmodal_noise = mix(colored_modal_noise * noise_level, modal_noise, clamp(noise_spectral_amount, 0, 1));\n\nvoice_scale = 1 / sqrt(max(mix_voices, 1));\nsig = mix(partials, modal_noise, clamp(noise_resonator_mix, 0, 1));\n\nout1 = sig * amp * output_ceiling * voice_scale;\nout2 = e0 + e1 + e2 + e3 + e4 + e5 + e6 + e7 + e8 + e9 + e10 + e11 + e12 + e13 + e14 + e15;\nout3 = freq;\n",
                    "fontface": 0,
                    "fontname": "<Monospaced>",
                    "fontsize": 12.0,
                    "id": "obj-39",
                    "maxclass": "gen.codebox~",
                    "numinlets": 1,
                    "numoutlets": 3,
                    "outlettype": [
                        "signal",
                        "signal",
                        "signal"
                    ],
                    "patching_rect": [
                        212.0,
                        387.0,
                        141.0,
                        31.0
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-42",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [
                        "signal"
                    ],
                    "patching_rect": [
                        212.0,
                        337.0,
                        31.0,
                        22.0
                    ],
                    "text": "sig~"
                }
            },
            {
                "box": {
                    "format": 6,
                    "id": "obj-58",
                    "maxclass": "flonum",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        "bang"
                    ],
                    "parameter_enable": 0,
                    "patching_rect": [
                        211.0,
                        293.0,
                        50.0,
                        22.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        102.0,
                        118.0,
                        50.0,
                        22.0
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-14",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        96.0,
                        333.0,
                        79.0,
                        22.0
                    ],
                    "text": "prepend amp"
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
                        96.0,
                        306.0,
                        50.0,
                        22.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        35.0,
                        148.0,
                        50.0,
                        22.0
                    ]
                }
            },
            {
                "box": {
                    "code": "// QMW Density Field Quantum Resonator 16\n//\n// Gen~ codebox.\n// in1 is the carrier frequency in Hz.\n// m0..m15 excite sixteen resonant partials.\n// ph0..ph15 set smoothed per-partial timing/phase.\n// s0..s15 set lifetime: fast lanes flash, slow lanes ring.\n// h0..h15 are partial ratios. Defaults are harmonic 1..16, but these can\n// later be replaced by Hamiltonian energy-gap ratios.\n\nParam m0(0);\nParam m1(0);\nParam m2(0);\nParam m3(0);\nParam m4(0);\nParam m5(0);\nParam m6(0);\nParam m7(0);\nParam m8(0);\nParam m9(0);\nParam m10(0);\nParam m11(0);\nParam m12(0);\nParam m13(0);\nParam m14(0);\nParam m15(0);\n\nParam ph0(0);\nParam ph1(0);\nParam ph2(0);\nParam ph3(0);\nParam ph4(0);\nParam ph5(0);\nParam ph6(0);\nParam ph7(0);\nParam ph8(0);\nParam ph9(0);\nParam ph10(0);\nParam ph11(0);\nParam ph12(0);\nParam ph13(0);\nParam ph14(0);\nParam ph15(0);\n\nParam s0(0);\nParam s1(0);\nParam s2(0);\nParam s3(0);\nParam s4(0);\nParam s5(0);\nParam s6(0);\nParam s7(0);\nParam s8(0);\nParam s9(0);\nParam s10(0);\nParam s11(0);\nParam s12(0);\nParam s13(0);\nParam s14(0);\nParam s15(0);\n\nParam h0(1);\nParam h1(2);\nParam h2(3);\nParam h3(4);\nParam h4(5);\nParam h5(6);\nParam h6(7);\nParam h7(8);\nParam h8(9);\nParam h9(10);\nParam h10(11);\nParam h11(12);\nParam h12(13);\nParam h13(14);\nParam h14(15);\nParam h15(16);\n\nParam purity(1);\nParam entropy(0);\nParam coherence(0);\nParam amp(0.2);\nParam default_freq(55);\nParam attack_ms(350);\nParam slow_decay_ms(3500);\nParam fast_decay_ms(900);\nParam phase_smooth_ms(4000);\nParam magnitude_smooth_ms(2500);\nParam brightness(0.65);\nParam mix_voices(4);\nParam output_ceiling(0.85);\nParam noise_resonator_mix(0.45);\nParam noise_amount(0.28);\nParam noise_floor(0);\nParam noise_color(0.72);\nParam noise_decay_ms(45);\nParam noise_spectral_amount(0.75);\nParam noise_spectral_gain(2.5);\nParam noise_spectral_base_hz(55);\nParam noise_spectral_q(7);\nParam quantum_pulse(0);\nParam quantum_noise_variation(0.25);\nParam quantum_brightness(0.5);\nParam quantum_event_decay_ms(1200);\nHistory quantum_pulse_z(0);\nHistory quantum_event_env(0);\nHistory modal_noise_lp(0);\nHistory nb0(0); History nl0(0);\nHistory nb1(0); History nl1(0);\nHistory nb2(0); History nl2(0);\nHistory nb3(0); History nl3(0);\nHistory nb4(0); History nl4(0);\nHistory nb5(0); History nl5(0);\nHistory nb6(0); History nl6(0);\nHistory nb7(0); History nl7(0);\nHistory nb8(0); History nl8(0);\nHistory nb9(0); History nl9(0);\nHistory nb10(0); History nl10(0);\nHistory nb11(0); History nl11(0);\nHistory nb12(0); History nl12(0);\nHistory nb13(0); History nl13(0);\nHistory nb14(0); History nl14(0);\nHistory nb15(0); History nl15(0);\n\nHistory p0(0);\nHistory p1(0);\nHistory p2(0);\nHistory p3(0);\nHistory p4(0);\nHistory p5(0);\nHistory p6(0);\nHistory p7(0);\nHistory p8(0);\nHistory p9(0);\nHistory p10(0);\nHistory p11(0);\nHistory p12(0);\nHistory p13(0);\nHistory p14(0);\nHistory p15(0);\n\nHistory e0(0);\nHistory e1(0);\nHistory e2(0);\nHistory e3(0);\nHistory e4(0);\nHistory e5(0);\nHistory e6(0);\nHistory e7(0);\nHistory e8(0);\nHistory e9(0);\nHistory e10(0);\nHistory e11(0);\nHistory e12(0);\nHistory e13(0);\nHistory e14(0);\nHistory e15(0);\n\nHistory sm0(0);\nHistory sm1(0);\nHistory sm2(0);\nHistory sm3(0);\nHistory sm4(0);\nHistory sm5(0);\nHistory sm6(0);\nHistory sm7(0);\nHistory sm8(0);\nHistory sm9(0);\nHistory sm10(0);\nHistory sm11(0);\nHistory sm12(0);\nHistory sm13(0);\nHistory sm14(0);\nHistory sm15(0);\n\nHistory sph0(0);\nHistory sph1(0);\nHistory sph2(0);\nHistory sph3(0);\nHistory sph4(0);\nHistory sph5(0);\nHistory sph6(0);\nHistory sph7(0);\nHistory sph8(0);\nHistory sph9(0);\nHistory sph10(0);\nHistory sph11(0);\nHistory sph12(0);\nHistory sph13(0);\nHistory sph14(0);\nHistory sph15(0);\n\nfreq = (in1 > 0) * in1 + (in1 <= 0) * default_freq;\npur = clamp(purity, 0, 1);\nent = clamp(entropy, 0, 1);\ncoh = clamp(coherence, 0, 1);\n\nmag_ms = max(magnitude_smooth_ms, 0.1);\nmag_coeff = exp(-1 / (mag_ms * 0.001 * samplerate));\n\ntm0 = clamp(m0, 0, 1);\ntm1 = clamp(m1, 0, 1);\ntm2 = clamp(m2, 0, 1);\ntm3 = clamp(m3, 0, 1);\ntm4 = clamp(m4, 0, 1);\ntm5 = clamp(m5, 0, 1);\ntm6 = clamp(m6, 0, 1);\ntm7 = clamp(m7, 0, 1);\ntm8 = clamp(m8, 0, 1);\ntm9 = clamp(m9, 0, 1);\ntm10 = clamp(m10, 0, 1);\ntm11 = clamp(m11, 0, 1);\ntm12 = clamp(m12, 0, 1);\ntm13 = clamp(m13, 0, 1);\ntm14 = clamp(m14, 0, 1);\ntm15 = clamp(m15, 0, 1);\n\nsm0 = tm0 + mag_coeff * (sm0 - tm0);\nsm1 = tm1 + mag_coeff * (sm1 - tm1);\nsm2 = tm2 + mag_coeff * (sm2 - tm2);\nsm3 = tm3 + mag_coeff * (sm3 - tm3);\nsm4 = tm4 + mag_coeff * (sm4 - tm4);\nsm5 = tm5 + mag_coeff * (sm5 - tm5);\nsm6 = tm6 + mag_coeff * (sm6 - tm6);\nsm7 = tm7 + mag_coeff * (sm7 - tm7);\nsm8 = tm8 + mag_coeff * (sm8 - tm8);\nsm9 = tm9 + mag_coeff * (sm9 - tm9);\nsm10 = tm10 + mag_coeff * (sm10 - tm10);\nsm11 = tm11 + mag_coeff * (sm11 - tm11);\nsm12 = tm12 + mag_coeff * (sm12 - tm12);\nsm13 = tm13 + mag_coeff * (sm13 - tm13);\nsm14 = tm14 + mag_coeff * (sm14 - tm14);\nsm15 = tm15 + mag_coeff * (sm15 - tm15);\n\nphase_ms = max(phase_smooth_ms, 0.1);\nphase_coeff = exp(-1 / (phase_ms * 0.001 * samplerate));\n\ndph0 = atan2(sin(ph0 - sph0), cos(ph0 - sph0));\ndph1 = atan2(sin(ph1 - sph1), cos(ph1 - sph1));\ndph2 = atan2(sin(ph2 - sph2), cos(ph2 - sph2));\ndph3 = atan2(sin(ph3 - sph3), cos(ph3 - sph3));\ndph4 = atan2(sin(ph4 - sph4), cos(ph4 - sph4));\ndph5 = atan2(sin(ph5 - sph5), cos(ph5 - sph5));\ndph6 = atan2(sin(ph6 - sph6), cos(ph6 - sph6));\ndph7 = atan2(sin(ph7 - sph7), cos(ph7 - sph7));\ndph8 = atan2(sin(ph8 - sph8), cos(ph8 - sph8));\ndph9 = atan2(sin(ph9 - sph9), cos(ph9 - sph9));\ndph10 = atan2(sin(ph10 - sph10), cos(ph10 - sph10));\ndph11 = atan2(sin(ph11 - sph11), cos(ph11 - sph11));\ndph12 = atan2(sin(ph12 - sph12), cos(ph12 - sph12));\ndph13 = atan2(sin(ph13 - sph13), cos(ph13 - sph13));\ndph14 = atan2(sin(ph14 - sph14), cos(ph14 - sph14));\ndph15 = atan2(sin(ph15 - sph15), cos(ph15 - sph15));\n\nsph0 = sph0 + (1 - phase_coeff) * dph0;\nsph1 = sph1 + (1 - phase_coeff) * dph1;\nsph2 = sph2 + (1 - phase_coeff) * dph2;\nsph3 = sph3 + (1 - phase_coeff) * dph3;\nsph4 = sph4 + (1 - phase_coeff) * dph4;\nsph5 = sph5 + (1 - phase_coeff) * dph5;\nsph6 = sph6 + (1 - phase_coeff) * dph6;\nsph7 = sph7 + (1 - phase_coeff) * dph7;\nsph8 = sph8 + (1 - phase_coeff) * dph8;\nsph9 = sph9 + (1 - phase_coeff) * dph9;\nsph10 = sph10 + (1 - phase_coeff) * dph10;\nsph11 = sph11 + (1 - phase_coeff) * dph11;\nsph12 = sph12 + (1 - phase_coeff) * dph12;\nsph13 = sph13 + (1 - phase_coeff) * dph13;\nsph14 = sph14 + (1 - phase_coeff) * dph14;\nsph15 = sph15 + (1 - phase_coeff) * dph15;\n\natk_ms = max(attack_ms * mix(1.35, 0.65, coh), 0.1);\natk_coeff = exp(-1 / (atk_ms * 0.001 * samplerate));\n\nspd0 = clamp(abs(s0), 0, 1);\nspd1 = clamp(abs(s1), 0, 1);\nspd2 = clamp(abs(s2), 0, 1);\nspd3 = clamp(abs(s3), 0, 1);\nspd4 = clamp(abs(s4), 0, 1);\nspd5 = clamp(abs(s5), 0, 1);\nspd6 = clamp(abs(s6), 0, 1);\nspd7 = clamp(abs(s7), 0, 1);\nspd8 = clamp(abs(s8), 0, 1);\nspd9 = clamp(abs(s9), 0, 1);\nspd10 = clamp(abs(s10), 0, 1);\nspd11 = clamp(abs(s11), 0, 1);\nspd12 = clamp(abs(s12), 0, 1);\nspd13 = clamp(abs(s13), 0, 1);\nspd14 = clamp(abs(s14), 0, 1);\nspd15 = clamp(abs(s15), 0, 1);\n\ndec0 = mix(slow_decay_ms, fast_decay_ms, spd0);\ndec1 = mix(slow_decay_ms, fast_decay_ms, spd1);\ndec2 = mix(slow_decay_ms, fast_decay_ms, spd2);\ndec3 = mix(slow_decay_ms, fast_decay_ms, spd3);\ndec4 = mix(slow_decay_ms, fast_decay_ms, spd4);\ndec5 = mix(slow_decay_ms, fast_decay_ms, spd5);\ndec6 = mix(slow_decay_ms, fast_decay_ms, spd6);\ndec7 = mix(slow_decay_ms, fast_decay_ms, spd7);\ndec8 = mix(slow_decay_ms, fast_decay_ms, spd8);\ndec9 = mix(slow_decay_ms, fast_decay_ms, spd9);\ndec10 = mix(slow_decay_ms, fast_decay_ms, spd10);\ndec11 = mix(slow_decay_ms, fast_decay_ms, spd11);\ndec12 = mix(slow_decay_ms, fast_decay_ms, spd12);\ndec13 = mix(slow_decay_ms, fast_decay_ms, spd13);\ndec14 = mix(slow_decay_ms, fast_decay_ms, spd14);\ndec15 = mix(slow_decay_ms, fast_decay_ms, spd15);\n\ndc0 = exp(-1 / (max(dec0, 0.1) * 0.001 * samplerate));\ndc1 = exp(-1 / (max(dec1, 0.1) * 0.001 * samplerate));\ndc2 = exp(-1 / (max(dec2, 0.1) * 0.001 * samplerate));\ndc3 = exp(-1 / (max(dec3, 0.1) * 0.001 * samplerate));\ndc4 = exp(-1 / (max(dec4, 0.1) * 0.001 * samplerate));\ndc5 = exp(-1 / (max(dec5, 0.1) * 0.001 * samplerate));\ndc6 = exp(-1 / (max(dec6, 0.1) * 0.001 * samplerate));\ndc7 = exp(-1 / (max(dec7, 0.1) * 0.001 * samplerate));\ndc8 = exp(-1 / (max(dec8, 0.1) * 0.001 * samplerate));\ndc9 = exp(-1 / (max(dec9, 0.1) * 0.001 * samplerate));\ndc10 = exp(-1 / (max(dec10, 0.1) * 0.001 * samplerate));\ndc11 = exp(-1 / (max(dec11, 0.1) * 0.001 * samplerate));\ndc12 = exp(-1 / (max(dec12, 0.1) * 0.001 * samplerate));\ndc13 = exp(-1 / (max(dec13, 0.1) * 0.001 * samplerate));\ndc14 = exp(-1 / (max(dec14, 0.1) * 0.001 * samplerate));\ndc15 = exp(-1 / (max(dec15, 0.1) * 0.001 * samplerate));\n\n// Higher entropy lifts weaker modes. Higher purity makes excitation more selective.\nexc_shape = mix(0.55, 1.6, pur);\nt0 = pow(sm0 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt1 = pow(sm1 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt2 = pow(sm2 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt3 = pow(sm3 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt4 = pow(sm4 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt5 = pow(sm5 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt6 = pow(sm6 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt7 = pow(sm7 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt8 = pow(sm8 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt9 = pow(sm9 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt10 = pow(sm10 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt11 = pow(sm11 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt12 = pow(sm12 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt13 = pow(sm13 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt14 = pow(sm14 + 0.00001, exc_shape) * mix(0.35, 1, ent);\nt15 = pow(sm15 + 0.00001, exc_shape) * mix(0.35, 1, ent);\n\ne0 = (t0 > e0) * (t0 + atk_coeff * (e0 - t0)) + (t0 <= e0) * (t0 + dc0 * (e0 - t0));\ne1 = (t1 > e1) * (t1 + atk_coeff * (e1 - t1)) + (t1 <= e1) * (t1 + dc1 * (e1 - t1));\ne2 = (t2 > e2) * (t2 + atk_coeff * (e2 - t2)) + (t2 <= e2) * (t2 + dc2 * (e2 - t2));\ne3 = (t3 > e3) * (t3 + atk_coeff * (e3 - t3)) + (t3 <= e3) * (t3 + dc3 * (e3 - t3));\ne4 = (t4 > e4) * (t4 + atk_coeff * (e4 - t4)) + (t4 <= e4) * (t4 + dc4 * (e4 - t4));\ne5 = (t5 > e5) * (t5 + atk_coeff * (e5 - t5)) + (t5 <= e5) * (t5 + dc5 * (e5 - t5));\ne6 = (t6 > e6) * (t6 + atk_coeff * (e6 - t6)) + (t6 <= e6) * (t6 + dc6 * (e6 - t6));\ne7 = (t7 > e7) * (t7 + atk_coeff * (e7 - t7)) + (t7 <= e7) * (t7 + dc7 * (e7 - t7));\ne8 = (t8 > e8) * (t8 + atk_coeff * (e8 - t8)) + (t8 <= e8) * (t8 + dc8 * (e8 - t8));\ne9 = (t9 > e9) * (t9 + atk_coeff * (e9 - t9)) + (t9 <= e9) * (t9 + dc9 * (e9 - t9));\ne10 = (t10 > e10) * (t10 + atk_coeff * (e10 - t10)) + (t10 <= e10) * (t10 + dc10 * (e10 - t10));\ne11 = (t11 > e11) * (t11 + atk_coeff * (e11 - t11)) + (t11 <= e11) * (t11 + dc11 * (e11 - t11));\ne12 = (t12 > e12) * (t12 + atk_coeff * (e12 - t12)) + (t12 <= e12) * (t12 + dc12 * (e12 - t12));\ne13 = (t13 > e13) * (t13 + atk_coeff * (e13 - t13)) + (t13 <= e13) * (t13 + dc13 * (e13 - t13));\ne14 = (t14 > e14) * (t14 + atk_coeff * (e14 - t14)) + (t14 <= e14) * (t14 + dc14 * (e14 - t14));\ne15 = (t15 > e15) * (t15 + atk_coeff * (e15 - t15)) + (t15 <= e15) * (t15 + dc15 * (e15 - t15));\n\nbright = clamp(brightness + ent * 0.18 + (quantum_brightness - 0.5) * 0.55, 0, 1);\n\np0 = fract(p0 + freq * max(h0, 0.01) / samplerate);\np1 = fract(p1 + freq * max(h1, 0.01) / samplerate);\np2 = fract(p2 + freq * max(h2, 0.01) / samplerate);\np3 = fract(p3 + freq * max(h3, 0.01) / samplerate);\np4 = fract(p4 + freq * max(h4, 0.01) / samplerate);\np5 = fract(p5 + freq * max(h5, 0.01) / samplerate);\np6 = fract(p6 + freq * max(h6, 0.01) / samplerate);\np7 = fract(p7 + freq * max(h7, 0.01) / samplerate);\np8 = fract(p8 + freq * max(h8, 0.01) / samplerate);\np9 = fract(p9 + freq * max(h9, 0.01) / samplerate);\np10 = fract(p10 + freq * max(h10, 0.01) / samplerate);\np11 = fract(p11 + freq * max(h11, 0.01) / samplerate);\np12 = fract(p12 + freq * max(h12, 0.01) / samplerate);\np13 = fract(p13 + freq * max(h13, 0.01) / samplerate);\np14 = fract(p14 + freq * max(h14, 0.01) / samplerate);\np15 = fract(p15 + freq * max(h15, 0.01) / samplerate);\n\ntwopi = 6.283185307179586;\npartials =\n    e0 * sin(twopi * p0 + sph0) / pow(max(h0, 1), bright) +\n    e1 * sin(twopi * p1 + sph1) / pow(max(h1, 1), bright) +\n    e2 * sin(twopi * p2 + sph2) / pow(max(h2, 1), bright) +\n    e3 * sin(twopi * p3 + sph3) / pow(max(h3, 1), bright) +\n    e4 * sin(twopi * p4 + sph4) / pow(max(h4, 1), bright) +\n    e5 * sin(twopi * p5 + sph5) / pow(max(h5, 1), bright) +\n    e6 * sin(twopi * p6 + sph6) / pow(max(h6, 1), bright) +\n    e7 * sin(twopi * p7 + sph7) / pow(max(h7, 1), bright) +\n    e8 * sin(twopi * p8 + sph8) / pow(max(h8, 1), bright) +\n    e9 * sin(twopi * p9 + sph9) / pow(max(h9, 1), bright) +\n    e10 * sin(twopi * p10 + sph10) / pow(max(h10, 1), bright) +\n    e11 * sin(twopi * p11 + sph11) / pow(max(h11, 1), bright) +\n    e12 * sin(twopi * p12 + sph12) / pow(max(h12, 1), bright) +\n    e13 * sin(twopi * p13 + sph13) / pow(max(h13, 1), bright) +\n    e14 * sin(twopi * p14 + sph14) / pow(max(h14, 1), bright) +\n    e15 * sin(twopi * p15 + sph15) / pow(max(h15, 1), bright);\n\nraw_modal_noise = noise();\nnoise_color_coeff = exp(-1 / (max(noise_decay_ms, 0.1) * 0.001 * samplerate));\nmodal_noise_lp = raw_modal_noise + noise_color_coeff * (modal_noise_lp - raw_modal_noise);\ncolored_modal_noise = mix(modal_noise_lp, raw_modal_noise, clamp(noise_color, 0, 1));\nquantum_trigger = (quantum_pulse > 0.5) * (quantum_pulse_z <= 0.5);\nquantum_pulse_z = quantum_pulse;\nquantum_decay_coeff = exp(-1 / (max(quantum_event_decay_ms, 1) * 0.001 * samplerate));\nquantum_event_env = quantum_trigger + (1 - quantum_trigger) * quantum_event_env * quantum_decay_coeff;\nnoise_level = (clamp(noise_floor, 0, 0.25) + 0.25 * clamp(noise_amount, 0, 1))\n    * clamp(quantum_noise_variation, 0, 1)\n    * (0.06 + 0.94 * clamp(quantum_event_env, 0, 1));\nnoise_input = colored_modal_noise * noise_level;\nmodal_q_eff = clamp(noise_spectral_q * 4 * mix(0.72, 1.45, pur), 2, 120);\nnf0 = clamp(freq * max(h0, 0.01), max(20, noise_spectral_base_hz * 0.25), samplerate * 0.45);\nng0 = tan(3.141592653589793 * nf0 / samplerate);\nna0 = 1 / (1 + ng0 * (ng0 + 1 / modal_q_eff));\nnv0 = na0 * (nb0 + ng0 * (noise_input - nl0));\nnlv0 = nl0 + ng0 * nv0;\nnb0 = 2 * nv0 - nb0;\nnl0 = 2 * nlv0 - nl0;\nnf1 = clamp(freq * max(h1, 0.01), max(20, noise_spectral_base_hz * 0.25), samplerate * 0.45);\nng1 = tan(3.141592653589793 * nf1 / samplerate);\nna1 = 1 / (1 + ng1 * (ng1 + 1 / modal_q_eff));\nnv1 = na1 * (nb1 + ng1 * (noise_input - nl1));\nnlv1 = nl1 + ng1 * nv1;\nnb1 = 2 * nv1 - nb1;\nnl1 = 2 * nlv1 - nl1;\nnf2 = clamp(freq * max(h2, 0.01), max(20, noise_spectral_base_hz * 0.25), samplerate * 0.45);\nng2 = tan(3.141592653589793 * nf2 / samplerate);\nna2 = 1 / (1 + ng2 * (ng2 + 1 / modal_q_eff));\nnv2 = na2 * (nb2 + ng2 * (noise_input - nl2));\nnlv2 = nl2 + ng2 * nv2;\nnb2 = 2 * nv2 - nb2;\nnl2 = 2 * nlv2 - nl2;\nnf3 = clamp(freq * max(h3, 0.01), max(20, noise_spectral_base_hz * 0.25), samplerate * 0.45);\nng3 = tan(3.141592653589793 * nf3 / samplerate);\nna3 = 1 / (1 + ng3 * (ng3 + 1 / modal_q_eff));\nnv3 = na3 * (nb3 + ng3 * (noise_input - nl3));\nnlv3 = nl3 + ng3 * nv3;\nnb3 = 2 * nv3 - nb3;\nnl3 = 2 * nlv3 - nl3;\nnf4 = clamp(freq * max(h4, 0.01), max(20, noise_spectral_base_hz * 0.25), samplerate * 0.45);\nng4 = tan(3.141592653589793 * nf4 / samplerate);\nna4 = 1 / (1 + ng4 * (ng4 + 1 / modal_q_eff));\nnv4 = na4 * (nb4 + ng4 * (noise_input - nl4));\nnlv4 = nl4 + ng4 * nv4;\nnb4 = 2 * nv4 - nb4;\nnl4 = 2 * nlv4 - nl4;\nnf5 = clamp(freq * max(h5, 0.01), max(20, noise_spectral_base_hz * 0.25), samplerate * 0.45);\nng5 = tan(3.141592653589793 * nf5 / samplerate);\nna5 = 1 / (1 + ng5 * (ng5 + 1 / modal_q_eff));\nnv5 = na5 * (nb5 + ng5 * (noise_input - nl5));\nnlv5 = nl5 + ng5 * nv5;\nnb5 = 2 * nv5 - nb5;\nnl5 = 2 * nlv5 - nl5;\nnf6 = clamp(freq * max(h6, 0.01), max(20, noise_spectral_base_hz * 0.25), samplerate * 0.45);\nng6 = tan(3.141592653589793 * nf6 / samplerate);\nna6 = 1 / (1 + ng6 * (ng6 + 1 / modal_q_eff));\nnv6 = na6 * (nb6 + ng6 * (noise_input - nl6));\nnlv6 = nl6 + ng6 * nv6;\nnb6 = 2 * nv6 - nb6;\nnl6 = 2 * nlv6 - nl6;\nnf7 = clamp(freq * max(h7, 0.01), max(20, noise_spectral_base_hz * 0.25), samplerate * 0.45);\nng7 = tan(3.141592653589793 * nf7 / samplerate);\nna7 = 1 / (1 + ng7 * (ng7 + 1 / modal_q_eff));\nnv7 = na7 * (nb7 + ng7 * (noise_input - nl7));\nnlv7 = nl7 + ng7 * nv7;\nnb7 = 2 * nv7 - nb7;\nnl7 = 2 * nlv7 - nl7;\nnf8 = clamp(freq * max(h8, 0.01), max(20, noise_spectral_base_hz * 0.25), samplerate * 0.45);\nng8 = tan(3.141592653589793 * nf8 / samplerate);\nna8 = 1 / (1 + ng8 * (ng8 + 1 / modal_q_eff));\nnv8 = na8 * (nb8 + ng8 * (noise_input - nl8));\nnlv8 = nl8 + ng8 * nv8;\nnb8 = 2 * nv8 - nb8;\nnl8 = 2 * nlv8 - nl8;\nnf9 = clamp(freq * max(h9, 0.01), max(20, noise_spectral_base_hz * 0.25), samplerate * 0.45);\nng9 = tan(3.141592653589793 * nf9 / samplerate);\nna9 = 1 / (1 + ng9 * (ng9 + 1 / modal_q_eff));\nnv9 = na9 * (nb9 + ng9 * (noise_input - nl9));\nnlv9 = nl9 + ng9 * nv9;\nnb9 = 2 * nv9 - nb9;\nnl9 = 2 * nlv9 - nl9;\nnf10 = clamp(freq * max(h10, 0.01), max(20, noise_spectral_base_hz * 0.25), samplerate * 0.45);\nng10 = tan(3.141592653589793 * nf10 / samplerate);\nna10 = 1 / (1 + ng10 * (ng10 + 1 / modal_q_eff));\nnv10 = na10 * (nb10 + ng10 * (noise_input - nl10));\nnlv10 = nl10 + ng10 * nv10;\nnb10 = 2 * nv10 - nb10;\nnl10 = 2 * nlv10 - nl10;\nnf11 = clamp(freq * max(h11, 0.01), max(20, noise_spectral_base_hz * 0.25), samplerate * 0.45);\nng11 = tan(3.141592653589793 * nf11 / samplerate);\nna11 = 1 / (1 + ng11 * (ng11 + 1 / modal_q_eff));\nnv11 = na11 * (nb11 + ng11 * (noise_input - nl11));\nnlv11 = nl11 + ng11 * nv11;\nnb11 = 2 * nv11 - nb11;\nnl11 = 2 * nlv11 - nl11;\nnf12 = clamp(freq * max(h12, 0.01), max(20, noise_spectral_base_hz * 0.25), samplerate * 0.45);\nng12 = tan(3.141592653589793 * nf12 / samplerate);\nna12 = 1 / (1 + ng12 * (ng12 + 1 / modal_q_eff));\nnv12 = na12 * (nb12 + ng12 * (noise_input - nl12));\nnlv12 = nl12 + ng12 * nv12;\nnb12 = 2 * nv12 - nb12;\nnl12 = 2 * nlv12 - nl12;\nnf13 = clamp(freq * max(h13, 0.01), max(20, noise_spectral_base_hz * 0.25), samplerate * 0.45);\nng13 = tan(3.141592653589793 * nf13 / samplerate);\nna13 = 1 / (1 + ng13 * (ng13 + 1 / modal_q_eff));\nnv13 = na13 * (nb13 + ng13 * (noise_input - nl13));\nnlv13 = nl13 + ng13 * nv13;\nnb13 = 2 * nv13 - nb13;\nnl13 = 2 * nlv13 - nl13;\nnf14 = clamp(freq * max(h14, 0.01), max(20, noise_spectral_base_hz * 0.25), samplerate * 0.45);\nng14 = tan(3.141592653589793 * nf14 / samplerate);\nna14 = 1 / (1 + ng14 * (ng14 + 1 / modal_q_eff));\nnv14 = na14 * (nb14 + ng14 * (noise_input - nl14));\nnlv14 = nl14 + ng14 * nv14;\nnb14 = 2 * nv14 - nb14;\nnl14 = 2 * nlv14 - nl14;\nnf15 = clamp(freq * max(h15, 0.01), max(20, noise_spectral_base_hz * 0.25), samplerate * 0.45);\nng15 = tan(3.141592653589793 * nf15 / samplerate);\nna15 = 1 / (1 + ng15 * (ng15 + 1 / modal_q_eff));\nnv15 = na15 * (nb15 + ng15 * (noise_input - nl15));\nnlv15 = nl15 + ng15 * nv15;\nnb15 = 2 * nv15 - nb15;\nnl15 = 2 * nlv15 - nl15;\nmodal_noise = (\n    e0 * nv0 +\n    e1 * nv1 +\n    e2 * nv2 +\n    e3 * nv3 +\n    e4 * nv4 +\n    e5 * nv5 +\n    e6 * nv6 +\n    e7 * nv7 +\n    e8 * nv8 +\n    e9 * nv9 +\n    e10 * nv10 +\n    e11 * nv11 +\n    e12 * nv12 +\n    e13 * nv13 +\n    e14 * nv14 +\n    e15 * nv15\n) / sqrt(16);\nmodal_noise = tanh(modal_noise * clamp(noise_spectral_gain, 0, 8));\nmodal_noise = mix(colored_modal_noise * noise_level, modal_noise, clamp(noise_spectral_amount, 0, 1));\n\nvoice_scale = 1 / sqrt(max(mix_voices, 1));\nsig = mix(partials, modal_noise, clamp(noise_resonator_mix, 0, 1));\n\nout1 = sig * amp * output_ceiling * voice_scale;\nout2 = e0 + e1 + e2 + e3 + e4 + e5 + e6 + e7 + e8 + e9 + e10 + e11 + e12 + e13 + e14 + e15;\nout3 = freq;\n",
                    "fontface": 0,
                    "fontname": "<Monospaced>",
                    "fontsize": 12.0,
                    "id": "obj-13",
                    "maxclass": "gen.codebox~",
                    "numinlets": 1,
                    "numoutlets": 3,
                    "outlettype": [
                        "signal",
                        "signal",
                        "signal"
                    ],
                    "patching_rect": [
                        39.0,
                        391.5,
                        126.0,
                        22.0
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-12",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        346.0,
                        171.0,
                        111.0,
                        22.0
                    ],
                    "text": "prepend harmonics"
                }
            },
            {
                "box": {
                    "automatic": 1,
                    "id": "obj-49",
                    "maxclass": "scope~",
                    "numinlets": 2,
                    "numoutlets": 0,
                    "patching_rect": [
                        462.0,
                        562.0,
                        130.0,
                        130.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        455.0,
                        220.0,
                        130.0,
                        130.0
                    ]
                }
            },
            {
                "box": {
                    "automatic": 1,
                    "id": "obj-48",
                    "maxclass": "scope~",
                    "numinlets": 2,
                    "numoutlets": 0,
                    "patching_rect": [
                        324.0,
                        562.0,
                        130.0,
                        130.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        317.0,
                        220.0,
                        130.0,
                        130.0
                    ]
                }
            },
            {
                "box": {
                    "format": 6,
                    "id": "obj-40",
                    "maxclass": "flonum",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        "bang"
                    ],
                    "parameter_enable": 0,
                    "patching_rect": [
                        473.5,
                        449.0,
                        50.0,
                        22.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        161.0,
                        184.0,
                        50.0,
                        22.0
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-41",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        "signal"
                    ],
                    "patching_rect": [
                        416.0,
                        449.0,
                        34.0,
                        22.0
                    ],
                    "text": "*~ 1."
                }
            },
            {
                "box": {
                    "automatic": 1,
                    "id": "obj-38",
                    "maxclass": "scope~",
                    "numinlets": 2,
                    "numoutlets": 0,
                    "patching_rect": [
                        187.0,
                        562.0,
                        130.0,
                        130.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        180.0,
                        220.0,
                        130.0,
                        130.0
                    ]
                }
            },
            {
                "box": {
                    "format": 6,
                    "id": "obj-30",
                    "maxclass": "flonum",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        "bang"
                    ],
                    "parameter_enable": 0,
                    "patching_rect": [
                        257.5,
                        449.0,
                        50.0,
                        22.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        102.0,
                        188.0,
                        50.0,
                        22.0
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-32",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        "signal"
                    ],
                    "patching_rect": [
                        212.0,
                        455.0,
                        34.0,
                        22.0
                    ],
                    "text": "*~ 1."
                }
            },
            {
                "box": {
                    "id": "obj-15",
                    "linecount": 9,
                    "maxclass": "comment",
                    "numinlets": 1,
                    "numoutlets": 0,
                    "patching_rect": [
                        681.333353638649,
                        -5.66667914390564,
                        150.0,
                        127.0
                    ],
                    "text": "amp 0.2\nattack_ms 350\nslow_decay_ms 3500\nfast_decay_ms 900\nmagnitude_smooth_ms 2500\nphase_smooth_ms 4000\nbrightness 0.65\nmix_voices 4"
                }
            },
            {
                "box": {
                    "automatic": 1,
                    "id": "obj-11",
                    "maxclass": "scope~",
                    "numinlets": 2,
                    "numoutlets": 0,
                    "patching_rect": [
                        42.0,
                        562.0,
                        130.0,
                        130.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        35.0,
                        220.0,
                        130.0,
                        130.0
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-10",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        248.0,
                        171.0,
                        89.0,
                        22.0
                    ],
                    "text": "prepend phase"
                }
            },
            {
                "box": {
                    "id": "obj-8",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        154.0,
                        171.0,
                        89.0,
                        22.0
                    ],
                    "text": "prepend speed"
                }
            },
            {
                "box": {
                    "id": "obj-5",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        0.0,
                        177.0,
                        112.0,
                        22.0
                    ],
                    "text": "prepend magnitude"
                }
            },
            {
                "box": {
                    "id": "obj-74",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [
                        "signal"
                    ],
                    "patching_rect": [
                        39.0,
                        333.0,
                        31.0,
                        22.0
                    ],
                    "text": "sig~"
                }
            },
            {
                "box": {
                    "format": 6,
                    "id": "obj-75",
                    "maxclass": "flonum",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        "bang"
                    ],
                    "parameter_enable": 0,
                    "patching_rect": [
                        39.0,
                        306.0,
                        50.0,
                        22.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        35.0,
                        118.0,
                        50.0,
                        22.0
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-61",
                    "maxclass": "newobj",
                    "numinlets": 4,
                    "numoutlets": 4,
                    "outlettype": [
                        "",
                        "",
                        "",
                        ""
                    ],
                    "patching_rect": [
                        39.0,
                        219.0,
                        205.0,
                        22.0
                    ],
                    "saved_object_attributes": {
                        "filename": "qmw_density_field_to_resonator_local.js",
                        "parameter_enable": 0
                    },
                    "text": "js qmw_density_field_to_resonator_local.js"
                }
            },
            {
                "box": {
                    "format": 6,
                    "id": "obj-59",
                    "maxclass": "flonum",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        "bang"
                    ],
                    "parameter_enable": 0,
                    "patching_rect": [
                        82.0,
                        455.0,
                        50.0,
                        22.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        35.0,
                        188.0,
                        50.0,
                        22.0
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-57",
                    "maxclass": "newobj",
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        "signal"
                    ],
                    "patching_rect": [
                        39.0,
                        455.0,
                        34.0,
                        22.0
                    ],
                    "text": "*~ 1."
                }
            },
            {
                "box": {
                    "id": "obj-4",
                    "maxclass": "newobj",
                    "numinlets": 0,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "patching_rect": [
                        277.33334159851074,
                        12.000000357627869,
                        97.0,
                        22.0
                    ],
                    "text": "r qmw.osc.raw"
                }
            },
            {
                "box": {
                    "id": "obj-3",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        ""
                    ],
                    "patching_rect": [
                        277.33334159851074,
                        42.66666793823242,
                        98.0,
                        22.0
                    ],
                    "text": "OSC-route /qmw"
                }
            },
            {
                "box": {
                    "id": "obj-2",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        ""
                    ],
                    "patching_rect": [
                        277.33334159851074,
                        80.00000238418579,
                        139.0,
                        22.0
                    ],
                    "text": "OSC-route /density_field"
                }
            },
            {
                "box": {
                    "id": "obj-1",
                    "maxclass": "newobj",
                    "numinlets": 1,
                    "numoutlets": 8,
                    "outlettype": [
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        ""
                    ],
                    "patching_rect": [
                        213.3333396911621,
                        114.33332443237305,
                        415.0,
                        22.0
                    ],
                    "text": "OSC-route /speed /magnitude /phase /harmonics /entropy /purity /coherence"
                }
            },
            {
                "box": {
                    "id": "obj-qmw-osc-type-guard-1",
                    "maxclass": "newobj",
                    "numinlets": 5,
                    "numoutlets": 5,
                    "outlettype": [
                        "",
                        "",
                        "",
                        "",
                        ""
                    ],
                    "patching_rect": [
                        1190.0,
                        20.0,
                        162.0,
                        22.0
                    ],
                    "text": "route float int list symbol"
                }
            },
            {
                "box": {
                    "id": "obj-qmw-osc-type-guard-2",
                    "maxclass": "newobj",
                    "numinlets": 5,
                    "numoutlets": 5,
                    "outlettype": [
                        "",
                        "",
                        "",
                        "",
                        ""
                    ],
                    "patching_rect": [
                        1190.0,
                        50.0,
                        162.0,
                        22.0
                    ],
                    "text": "route float int list symbol"
                }
            },
            {
                "box": {
                    "id": "obj-qmw-osc-type-guard-3",
                    "maxclass": "newobj",
                    "numinlets": 5,
                    "numoutlets": 5,
                    "outlettype": [
                        "",
                        "",
                        "",
                        "",
                        ""
                    ],
                    "patching_rect": [
                        1190.0,
                        80.0,
                        162.0,
                        22.0
                    ],
                    "text": "route float int list symbol"
                }
            },
            {
                "box": {
                    "id": "obj-qmw-osc-type-guard-4",
                    "maxclass": "newobj",
                    "numinlets": 5,
                    "numoutlets": 5,
                    "outlettype": [
                        "",
                        "",
                        "",
                        "",
                        ""
                    ],
                    "patching_rect": [
                        1190.0,
                        110.0,
                        162.0,
                        22.0
                    ],
                    "text": "route float int list symbol"
                }
            },
            {
                "box": {
                    "id": "obj-qmw-osc-type-guard-5",
                    "maxclass": "newobj",
                    "numinlets": 5,
                    "numoutlets": 5,
                    "outlettype": [
                        "",
                        "",
                        "",
                        "",
                        ""
                    ],
                    "patching_rect": [
                        1190.0,
                        140.0,
                        162.0,
                        22.0
                    ],
                    "text": "route float int list symbol"
                }
            },
            {
                "box": {
                    "id": "obj-qmw-osc-type-guard-6",
                    "maxclass": "newobj",
                    "numinlets": 5,
                    "numoutlets": 5,
                    "outlettype": [
                        "",
                        "",
                        "",
                        "",
                        ""
                    ],
                    "patching_rect": [
                        1190.0,
                        170.0,
                        162.0,
                        22.0
                    ],
                    "text": "route float int list symbol"
                }
            },
            {
                "box": {
                    "id": "obj-163",
                    "maxclass": "newobj",
                    "text": "send~ qmw_qubit_0",
                    "patching_rect": [
                        900.0,
                        390.0,
                        142.0,
                        22.0
                    ],
                    "numinlets": 1,
                    "numoutlets": 0
                }
            },
            {
                "box": {
                    "id": "obj-164",
                    "maxclass": "newobj",
                    "text": "send~ qmw_qubit_1",
                    "patching_rect": [
                        900.0,
                        422.0,
                        142.0,
                        22.0
                    ],
                    "numinlets": 1,
                    "numoutlets": 0
                }
            },
            {
                "box": {
                    "id": "obj-165",
                    "maxclass": "newobj",
                    "text": "send~ qmw_qubit_2",
                    "patching_rect": [
                        900.0,
                        454.0,
                        142.0,
                        22.0
                    ],
                    "numinlets": 1,
                    "numoutlets": 0
                }
            },
            {
                "box": {
                    "id": "obj-166",
                    "maxclass": "newobj",
                    "text": "send~ qmw_qubit_3",
                    "patching_rect": [
                        900.0,
                        486.0,
                        142.0,
                        22.0
                    ],
                    "numinlets": 1,
                    "numoutlets": 0
                }
            },
            {
                "box": {
                    "id": "obj-167",
                    "maxclass": "message",
                    "text": "test",
                    "patching_rect": [
                        8.0,
                        10.0,
                        42.0,
                        22.0
                    ],
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-170",
                    "maxclass": "comment",
                    "text": "RESEED RESONATORS",
                    "patching_rect": [
                        55.0,
                        11.0,
                        145.0,
                        20.0
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-168",
                    "maxclass": "newobj",
                    "text": "loadbang",
                    "patching_rect": [
                        1090.0,
                        390.0,
                        62.0,
                        22.0
                    ],
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [
                        "bang"
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-169",
                    "maxclass": "newobj",
                    "text": "delay 250",
                    "patching_rect": [
                        1160.0,
                        390.0,
                        70.0,
                        22.0
                    ],
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        "bang"
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-171",
                    "maxclass": "newobj",
                    "text": "expr min(1., max(0., $f1 / 4.))",
                    "patching_rect": [
                        467.0,
                        143.0,
                        190.0,
                        22.0
                    ],
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [
                        "float"
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-172",
                    "maxclass": "newobj",
                    "text": "expr min(1., max(0., $f1 / 15.))",
                    "patching_rect": [
                        665.0,
                        143.0,
                        195.0,
                        22.0
                    ],
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [
                        "float"
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-173",
                    "maxclass": "newobj",
                    "text": "prepend purity",
                    "patching_rect": [
                        760.0,
                        171.0,
                        90.0,
                        22.0
                    ],
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ]
                }
            },
            {
                "box": {
                    "id": "obj-174",
                    "maxclass": "newobj",
                    "text": "delay 1500",
                    "patching_rect": [
                        1240.0,
                        390.0,
                        76.0,
                        22.0
                    ],
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        "bang"
                    ]
                }
            },
            {
                "box": {
                    "maxclass": "flonum",
                    "patching_rect": [
                        900.0,
                        525.0,
                        60.0,
                        22.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        310.0,
                        148.0,
                        60.0,
                        22.0
                    ],
                    "format": 6,
                    "parameter_enable": 0,
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        "bang"
                    ],
                    "id": "obj-175"
                }
            },
            {
                "box": {
                    "maxclass": "comment",
                    "text": "NOISE\u2192RESONATOR",
                    "patching_rect": [
                        900.0,
                        500.0,
                        150.0,
                        20.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        300.0,
                        125.0,
                        150.0,
                        20.0
                    ],
                    "numinlets": 1,
                    "numoutlets": 0,
                    "id": "obj-176"
                }
            },
            {
                "box": {
                    "maxclass": "newobj",
                    "text": "loadmess 0.45",
                    "patching_rect": [
                        970.0,
                        525.0,
                        94.0,
                        22.0
                    ],
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [
                        "float"
                    ],
                    "id": "obj-177"
                }
            },
            {
                "box": {
                    "maxclass": "newobj",
                    "text": "prepend noise_resonator_mix",
                    "patching_rect": [
                        1075.0,
                        525.0,
                        180.0,
                        22.0
                    ],
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "id": "obj-178"
                }
            },
            {
                "box": {
                    "maxclass": "newobj",
                    "text": "r qmw.resonator.noise",
                    "patching_rect": [
                        900.0,
                        565.0,
                        145.0,
                        22.0
                    ],
                    "numinlets": 0,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "id": "obj-179"
                }
            },
            {
                "box": {
                    "maxclass": "newobj",
                    "text": "route noise_amount noise_floor noise_color noise_decay_ms noise_spectral_amount noise_spectral_gain noise_spectral_base_hz noise_spectral_q",
                    "patching_rect": [
                        1055.0,
                        565.0,
                        670.0,
                        22.0
                    ],
                    "numinlets": 1,
                    "numoutlets": 9,
                    "outlettype": [
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        ""
                    ],
                    "id": "obj-180"
                }
            },
            {
                "box": {
                    "maxclass": "newobj",
                    "text": "prepend noise_amount",
                    "patching_rect": [
                        1055.0,
                        600.0,
                        80.0,
                        22.0
                    ],
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "id": "obj-181"
                }
            },
            {
                "box": {
                    "maxclass": "newobj",
                    "text": "prepend noise_floor",
                    "patching_rect": [
                        1137.0,
                        600.0,
                        80.0,
                        22.0
                    ],
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "id": "obj-182"
                }
            },
            {
                "box": {
                    "maxclass": "newobj",
                    "text": "prepend noise_color",
                    "patching_rect": [
                        1219.0,
                        600.0,
                        80.0,
                        22.0
                    ],
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "id": "obj-183"
                }
            },
            {
                "box": {
                    "maxclass": "newobj",
                    "text": "prepend noise_decay_ms",
                    "patching_rect": [
                        1301.0,
                        600.0,
                        80.0,
                        22.0
                    ],
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "id": "obj-184"
                }
            },
            {
                "box": {
                    "maxclass": "newobj",
                    "text": "prepend noise_spectral_amount",
                    "patching_rect": [
                        1383.0,
                        600.0,
                        80.0,
                        22.0
                    ],
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "id": "obj-185"
                }
            },
            {
                "box": {
                    "maxclass": "newobj",
                    "text": "prepend noise_spectral_gain",
                    "patching_rect": [
                        1465.0,
                        600.0,
                        80.0,
                        22.0
                    ],
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "id": "obj-186"
                }
            },
            {
                "box": {
                    "maxclass": "newobj",
                    "text": "prepend noise_spectral_base_hz",
                    "patching_rect": [
                        1547.0,
                        600.0,
                        80.0,
                        22.0
                    ],
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "id": "obj-187"
                }
            },
            {
                "box": {
                    "maxclass": "newobj",
                    "text": "prepend noise_spectral_q",
                    "patching_rect": [
                        1629.0,
                        600.0,
                        80.0,
                        22.0
                    ],
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "id": "obj-188"
                }
            },
            {
                "box": {
                    "maxclass": "newobj",
                    "text": "js qmw_four_qubit_event_engine_v1.js",
                    "patching_rect": [
                        900.0,
                        650.0,
                        225.0,
                        22.0
                    ],
                    "numinlets": 6,
                    "numoutlets": 4,
                    "outlettype": [
                        "",
                        "",
                        "",
                        ""
                    ],
                    "saved_object_attributes": {
                        "filename": "qmw_four_qubit_event_engine_v1.js",
                        "parameter_enable": 0
                    },
                    "id": "obj-189"
                }
            },
            {
                "box": {
                    "maxclass": "toggle",
                    "patching_rect": [
                        900.0,
                        685.0,
                        24.0,
                        24.0
                    ],
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [
                        "int"
                    ],
                    "parameter_enable": 0,
                    "id": "obj-190"
                }
            },
            {
                "box": {
                    "maxclass": "newobj",
                    "text": "loadmess 1",
                    "patching_rect": [
                        930.0,
                        685.0,
                        72.0,
                        22.0
                    ],
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [
                        "int"
                    ],
                    "id": "obj-191"
                }
            },
            {
                "box": {
                    "maxclass": "newobj",
                    "text": "qmetro 25",
                    "patching_rect": [
                        1010.0,
                        685.0,
                        72.0,
                        22.0
                    ],
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        "bang"
                    ],
                    "id": "obj-192"
                }
            },
            {
                "box": {
                    "maxclass": "newobj",
                    "text": "r qmw.pauli.correlations",
                    "patching_rect": [
                        1090.0,
                        685.0,
                        165.0,
                        22.0
                    ],
                    "numinlets": 0,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "id": "obj-193"
                }
            },
            {
                "box": {
                    "maxclass": "newobj",
                    "text": "route quantum_pulse",
                    "patching_rect": [
                        900.0,
                        725.0,
                        120.0,
                        22.0
                    ],
                    "numinlets": 2,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        ""
                    ],
                    "id": "obj-194"
                }
            },
            {
                "box": {
                    "maxclass": "newobj",
                    "text": "sel 1",
                    "patching_rect": [
                        900.0,
                        752.0,
                        38.0,
                        22.0
                    ],
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "bang",
                        ""
                    ],
                    "id": "obj-195"
                }
            },
            {
                "box": {
                    "maxclass": "button",
                    "patching_rect": [
                        945.0,
                        752.0,
                        24.0,
                        24.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        35.0,
                        88.0,
                        20.0,
                        20.0
                    ],
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [
                        "bang"
                    ],
                    "id": "obj-196"
                }
            },
            {
                "box": {
                    "maxclass": "newobj",
                    "text": "route quantum_pulse",
                    "patching_rect": [
                        1025.0,
                        725.0,
                        120.0,
                        22.0
                    ],
                    "numinlets": 2,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        ""
                    ],
                    "id": "obj-197"
                }
            },
            {
                "box": {
                    "maxclass": "newobj",
                    "text": "sel 1",
                    "patching_rect": [
                        1025.0,
                        752.0,
                        38.0,
                        22.0
                    ],
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "bang",
                        ""
                    ],
                    "id": "obj-198"
                }
            },
            {
                "box": {
                    "maxclass": "button",
                    "patching_rect": [
                        1070.0,
                        752.0,
                        24.0,
                        24.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        101.0,
                        88.0,
                        20.0,
                        20.0
                    ],
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [
                        "bang"
                    ],
                    "id": "obj-199"
                }
            },
            {
                "box": {
                    "maxclass": "newobj",
                    "text": "route quantum_pulse",
                    "patching_rect": [
                        1150.0,
                        725.0,
                        120.0,
                        22.0
                    ],
                    "numinlets": 2,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        ""
                    ],
                    "id": "obj-200"
                }
            },
            {
                "box": {
                    "maxclass": "newobj",
                    "text": "sel 1",
                    "patching_rect": [
                        1150.0,
                        752.0,
                        38.0,
                        22.0
                    ],
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "bang",
                        ""
                    ],
                    "id": "obj-201"
                }
            },
            {
                "box": {
                    "maxclass": "button",
                    "patching_rect": [
                        1195.0,
                        752.0,
                        24.0,
                        24.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        167.0,
                        88.0,
                        20.0,
                        20.0
                    ],
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [
                        "bang"
                    ],
                    "id": "obj-202"
                }
            },
            {
                "box": {
                    "maxclass": "newobj",
                    "text": "route quantum_pulse",
                    "patching_rect": [
                        1275.0,
                        725.0,
                        120.0,
                        22.0
                    ],
                    "numinlets": 2,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        ""
                    ],
                    "id": "obj-203"
                }
            },
            {
                "box": {
                    "maxclass": "newobj",
                    "text": "sel 1",
                    "patching_rect": [
                        1275.0,
                        752.0,
                        38.0,
                        22.0
                    ],
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "bang",
                        ""
                    ],
                    "id": "obj-204"
                }
            },
            {
                "box": {
                    "maxclass": "button",
                    "patching_rect": [
                        1320.0,
                        752.0,
                        24.0,
                        24.0
                    ],
                    "presentation": 1,
                    "presentation_rect": [
                        233.0,
                        88.0,
                        20.0,
                        20.0
                    ],
                    "numinlets": 1,
                    "numoutlets": 1,
                    "outlettype": [
                        "bang"
                    ],
                    "id": "obj-205"
                }
            },
            {
                "box": {
                    "maxclass": "newobj",
                    "text": "s qmw.qubit.grain.trigger",
                    "patching_rect": [
                        1430.0,
                        790.0,
                        175.0,
                        22.0
                    ],
                    "numinlets": 1,
                    "numoutlets": 0,
                    "id": "obj-206"
                }
            },
            {
                "box": {
                    "maxclass": "newobj",
                    "text": "route quantum_pulse",
                    "patching_rect": [
                        900.0,
                        790.0,
                        120.0,
                        22.0
                    ],
                    "numinlets": 2,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        ""
                    ],
                    "id": "obj-207"
                }
            },
            {
                "box": {
                    "maxclass": "newobj",
                    "text": "sel 1",
                    "patching_rect": [
                        900.0,
                        820.0,
                        38.0,
                        22.0
                    ],
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "bang",
                        ""
                    ],
                    "id": "obj-208"
                }
            },
            {
                "box": {
                    "maxclass": "message",
                    "text": "trigger 1. 900 0",
                    "patching_rect": [
                        945.0,
                        820.0,
                        120.0,
                        22.0
                    ],
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "id": "obj-209"
                }
            },
            {
                "box": {
                    "maxclass": "newobj",
                    "text": "route quantum_pulse",
                    "patching_rect": [
                        1030.0,
                        790.0,
                        120.0,
                        22.0
                    ],
                    "numinlets": 2,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        ""
                    ],
                    "id": "obj-210"
                }
            },
            {
                "box": {
                    "maxclass": "newobj",
                    "text": "sel 1",
                    "patching_rect": [
                        1030.0,
                        820.0,
                        38.0,
                        22.0
                    ],
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "bang",
                        ""
                    ],
                    "id": "obj-211"
                }
            },
            {
                "box": {
                    "maxclass": "message",
                    "text": "trigger 1. 900 1",
                    "patching_rect": [
                        1075.0,
                        820.0,
                        120.0,
                        22.0
                    ],
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "id": "obj-212"
                }
            },
            {
                "box": {
                    "maxclass": "newobj",
                    "text": "route quantum_pulse",
                    "patching_rect": [
                        1160.0,
                        790.0,
                        120.0,
                        22.0
                    ],
                    "numinlets": 2,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        ""
                    ],
                    "id": "obj-213"
                }
            },
            {
                "box": {
                    "maxclass": "newobj",
                    "text": "sel 1",
                    "patching_rect": [
                        1160.0,
                        820.0,
                        38.0,
                        22.0
                    ],
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "bang",
                        ""
                    ],
                    "id": "obj-214"
                }
            },
            {
                "box": {
                    "maxclass": "message",
                    "text": "trigger 1. 900 2",
                    "patching_rect": [
                        1205.0,
                        820.0,
                        120.0,
                        22.0
                    ],
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "id": "obj-215"
                }
            },
            {
                "box": {
                    "maxclass": "newobj",
                    "text": "route quantum_pulse",
                    "patching_rect": [
                        1290.0,
                        790.0,
                        120.0,
                        22.0
                    ],
                    "numinlets": 2,
                    "numoutlets": 2,
                    "outlettype": [
                        "",
                        ""
                    ],
                    "id": "obj-216"
                }
            },
            {
                "box": {
                    "maxclass": "newobj",
                    "text": "sel 1",
                    "patching_rect": [
                        1290.0,
                        820.0,
                        38.0,
                        22.0
                    ],
                    "numinlets": 1,
                    "numoutlets": 2,
                    "outlettype": [
                        "bang",
                        ""
                    ],
                    "id": "obj-217"
                }
            },
            {
                "box": {
                    "maxclass": "message",
                    "text": "trigger 1. 900 3",
                    "patching_rect": [
                        1335.0,
                        820.0,
                        120.0,
                        22.0
                    ],
                    "numinlets": 2,
                    "numoutlets": 1,
                    "outlettype": [
                        ""
                    ],
                    "id": "obj-218"
                }
            }
        ],
        "lines": [
            {
                "patchline": {
                    "destination": [
                        "obj-36",
                        1
                    ],
                    "order": 0,
                    "source": [
                        "obj-1",
                        6
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-45",
                        0
                    ],
                    "order": 0,
                    "source": [
                        "obj-1",
                        5
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-50",
                        1
                    ],
                    "order": 0,
                    "source": [
                        "obj-1",
                        4
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-78",
                        0
                    ],
                    "source": [
                        "obj-104",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-108",
                        0
                    ],
                    "source": [
                        "obj-106",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-106",
                        0
                    ],
                    "source": [
                        "obj-107",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-112",
                        0
                    ],
                    "source": [
                        "obj-108",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-108",
                        0
                    ],
                    "source": [
                        "obj-109",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-109",
                        0
                    ],
                    "source": [
                        "obj-110",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-112",
                        1
                    ],
                    "source": [
                        "obj-111",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-19",
                        0
                    ],
                    "order": 2,
                    "source": [
                        "obj-112",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-24",
                        0
                    ],
                    "order": 0,
                    "source": [
                        "obj-112",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-49",
                        0
                    ],
                    "order": 1,
                    "source": [
                        "obj-112",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-qmw-osc-type-guard-1",
                        0
                    ],
                    "source": [
                        "obj-121",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-qmw-osc-type-guard-2",
                        0
                    ],
                    "source": [
                        "obj-123",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-qmw-osc-type-guard-3",
                        0
                    ],
                    "source": [
                        "obj-124",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-qmw-osc-type-guard-4",
                        0
                    ],
                    "source": [
                        "obj-124",
                        1
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-57",
                        0
                    ],
                    "source": [
                        "obj-13",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-13",
                        0
                    ],
                    "source": [
                        "obj-14",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-154",
                        0
                    ],
                    "source": [
                        "obj-143",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-162",
                        0
                    ],
                    "source": [
                        "obj-149",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-156",
                        0
                    ],
                    "source": [
                        "obj-154",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-157",
                        0
                    ],
                    "source": [
                        "obj-154",
                        1
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-158",
                        0
                    ],
                    "source": [
                        "obj-154",
                        2
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
                        "obj-16",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-159",
                        0
                    ],
                    "source": [
                        "obj-162",
                        2
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-160",
                        0
                    ],
                    "source": [
                        "obj-162",
                        1
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-161",
                        0
                    ],
                    "source": [
                        "obj-162",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-qmw-osc-type-guard-5",
                        0
                    ],
                    "source": [
                        "obj-2",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-39",
                        0
                    ],
                    "source": [
                        "obj-21",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-21",
                        0
                    ],
                    "source": [
                        "obj-22",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-qmw-osc-type-guard-6",
                        0
                    ],
                    "source": [
                        "obj-3",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-32",
                        1
                    ],
                    "source": [
                        "obj-30",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-19",
                        0
                    ],
                    "order": 0,
                    "source": [
                        "obj-32",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-23",
                        0
                    ],
                    "order": 1,
                    "source": [
                        "obj-32",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-38",
                        0
                    ],
                    "order": 2,
                    "source": [
                        "obj-32",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-32",
                        0
                    ],
                    "source": [
                        "obj-39",
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
                        "obj-4",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-41",
                        1
                    ],
                    "source": [
                        "obj-40",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-25",
                        0
                    ],
                    "order": 0,
                    "source": [
                        "obj-41",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-48",
                        0
                    ],
                    "order": 1,
                    "source": [
                        "obj-41",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-9",
                        0
                    ],
                    "order": 2,
                    "source": [
                        "obj-41",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-39",
                        0
                    ],
                    "source": [
                        "obj-42",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-61",
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
                        "obj-61",
                        3
                    ],
                    "source": [
                        "obj-12",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-11",
                        0
                    ],
                    "order": 2,
                    "source": [
                        "obj-57",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-20",
                        0
                    ],
                    "order": 1,
                    "source": [
                        "obj-57",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-9",
                        0
                    ],
                    "order": 0,
                    "source": [
                        "obj-57",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-42",
                        0
                    ],
                    "source": [
                        "obj-58",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-57",
                        1
                    ],
                    "source": [
                        "obj-59",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-108",
                        0
                    ],
                    "order": 0,
                    "source": [
                        "obj-6",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-13",
                        0
                    ],
                    "order": 3,
                    "source": [
                        "obj-6",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-39",
                        0
                    ],
                    "order": 2,
                    "source": [
                        "obj-6",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-63",
                        0
                    ],
                    "order": 1,
                    "source": [
                        "obj-6",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-63",
                        0
                    ],
                    "source": [
                        "obj-60",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-13",
                        0
                    ],
                    "source": [
                        "obj-61",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-39",
                        0
                    ],
                    "source": [
                        "obj-61",
                        1
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-63",
                        0
                    ],
                    "source": [
                        "obj-61",
                        2
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-108",
                        0
                    ],
                    "source": [
                        "obj-61",
                        3
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-60",
                        0
                    ],
                    "source": [
                        "obj-62",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-41",
                        0
                    ],
                    "source": [
                        "obj-63",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-63",
                        0
                    ],
                    "source": [
                        "obj-64",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-64",
                        0
                    ],
                    "source": [
                        "obj-65",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-108",
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
                        "obj-13",
                        0
                    ],
                    "order": 3,
                    "source": [
                        "obj-7",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-39",
                        0
                    ],
                    "order": 2,
                    "source": [
                        "obj-7",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-63",
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
                        "obj-71",
                        0
                    ],
                    "source": [
                        "obj-70",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-108",
                        0
                    ],
                    "order": 0,
                    "source": [
                        "obj-71",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-13",
                        0
                    ],
                    "order": 3,
                    "source": [
                        "obj-71",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-39",
                        0
                    ],
                    "order": 2,
                    "source": [
                        "obj-71",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-63",
                        0
                    ],
                    "order": 1,
                    "source": [
                        "obj-71",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-13",
                        0
                    ],
                    "source": [
                        "obj-74",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-74",
                        0
                    ],
                    "source": [
                        "obj-75",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-108",
                        0
                    ],
                    "order": 0,
                    "source": [
                        "obj-78",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-13",
                        0
                    ],
                    "order": 3,
                    "source": [
                        "obj-78",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-39",
                        0
                    ],
                    "order": 2,
                    "source": [
                        "obj-78",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-63",
                        0
                    ],
                    "order": 1,
                    "source": [
                        "obj-78",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-122",
                        0
                    ],
                    "source": [
                        "obj-qmw-osc-type-guard-1",
                        4
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-124",
                        0
                    ],
                    "source": [
                        "obj-qmw-osc-type-guard-2",
                        4
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-143",
                        0
                    ],
                    "source": [
                        "obj-qmw-osc-type-guard-3",
                        4
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-149",
                        0
                    ],
                    "source": [
                        "obj-qmw-osc-type-guard-4",
                        4
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-1",
                        0
                    ],
                    "source": [
                        "obj-qmw-osc-type-guard-5",
                        4
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-121",
                        0
                    ],
                    "order": 0,
                    "source": [
                        "obj-qmw-osc-type-guard-6",
                        4
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-123",
                        0
                    ],
                    "order": 1,
                    "source": [
                        "obj-qmw-osc-type-guard-6",
                        4
                    ]
                }
            },
            {
                "patchline": {
                    "destination": [
                        "obj-2",
                        0
                    ],
                    "order": 2,
                    "source": [
                        "obj-qmw-osc-type-guard-6",
                        4
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-57",
                        0
                    ],
                    "destination": [
                        "obj-163",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-32",
                        0
                    ],
                    "destination": [
                        "obj-164",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-41",
                        0
                    ],
                    "destination": [
                        "obj-165",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-112",
                        0
                    ],
                    "destination": [
                        "obj-166",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-168",
                        0
                    ],
                    "destination": [
                        "obj-169",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-169",
                        0
                    ],
                    "destination": [
                        "obj-167",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-167",
                        0
                    ],
                    "destination": [
                        "obj-61",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-1",
                        0
                    ],
                    "destination": [
                        "obj-8",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-1",
                        1
                    ],
                    "destination": [
                        "obj-5",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-1",
                        2
                    ],
                    "destination": [
                        "obj-10",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-1",
                        3
                    ],
                    "destination": [
                        "obj-12",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-1",
                        4
                    ],
                    "destination": [
                        "obj-171",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-171",
                        0
                    ],
                    "destination": [
                        "obj-6",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-1",
                        6
                    ],
                    "destination": [
                        "obj-172",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-172",
                        0
                    ],
                    "destination": [
                        "obj-7",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-1",
                        5
                    ],
                    "destination": [
                        "obj-173",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-173",
                        0
                    ],
                    "destination": [
                        "obj-108",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-173",
                        0
                    ],
                    "destination": [
                        "obj-63",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-173",
                        0
                    ],
                    "destination": [
                        "obj-39",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-173",
                        0
                    ],
                    "destination": [
                        "obj-13",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-168",
                        0
                    ],
                    "destination": [
                        "obj-174",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-174",
                        0
                    ],
                    "destination": [
                        "obj-167",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-177",
                        0
                    ],
                    "destination": [
                        "obj-175",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-175",
                        0
                    ],
                    "destination": [
                        "obj-178",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-178",
                        0
                    ],
                    "destination": [
                        "obj-108",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-178",
                        0
                    ],
                    "destination": [
                        "obj-63",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-178",
                        0
                    ],
                    "destination": [
                        "obj-39",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-178",
                        0
                    ],
                    "destination": [
                        "obj-13",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-179",
                        0
                    ],
                    "destination": [
                        "obj-180",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-180",
                        0
                    ],
                    "destination": [
                        "obj-181",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-181",
                        0
                    ],
                    "destination": [
                        "obj-108",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-181",
                        0
                    ],
                    "destination": [
                        "obj-63",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-181",
                        0
                    ],
                    "destination": [
                        "obj-39",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-181",
                        0
                    ],
                    "destination": [
                        "obj-13",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-180",
                        1
                    ],
                    "destination": [
                        "obj-182",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-182",
                        0
                    ],
                    "destination": [
                        "obj-108",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-182",
                        0
                    ],
                    "destination": [
                        "obj-63",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-182",
                        0
                    ],
                    "destination": [
                        "obj-39",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-182",
                        0
                    ],
                    "destination": [
                        "obj-13",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-180",
                        2
                    ],
                    "destination": [
                        "obj-183",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-183",
                        0
                    ],
                    "destination": [
                        "obj-108",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-183",
                        0
                    ],
                    "destination": [
                        "obj-63",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-183",
                        0
                    ],
                    "destination": [
                        "obj-39",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-183",
                        0
                    ],
                    "destination": [
                        "obj-13",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-180",
                        3
                    ],
                    "destination": [
                        "obj-184",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-184",
                        0
                    ],
                    "destination": [
                        "obj-108",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-184",
                        0
                    ],
                    "destination": [
                        "obj-63",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-184",
                        0
                    ],
                    "destination": [
                        "obj-39",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-184",
                        0
                    ],
                    "destination": [
                        "obj-13",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-180",
                        4
                    ],
                    "destination": [
                        "obj-185",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-185",
                        0
                    ],
                    "destination": [
                        "obj-108",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-185",
                        0
                    ],
                    "destination": [
                        "obj-63",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-185",
                        0
                    ],
                    "destination": [
                        "obj-39",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-185",
                        0
                    ],
                    "destination": [
                        "obj-13",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-180",
                        5
                    ],
                    "destination": [
                        "obj-186",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-186",
                        0
                    ],
                    "destination": [
                        "obj-108",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-186",
                        0
                    ],
                    "destination": [
                        "obj-63",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-186",
                        0
                    ],
                    "destination": [
                        "obj-39",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-186",
                        0
                    ],
                    "destination": [
                        "obj-13",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-180",
                        6
                    ],
                    "destination": [
                        "obj-187",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-187",
                        0
                    ],
                    "destination": [
                        "obj-108",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-187",
                        0
                    ],
                    "destination": [
                        "obj-63",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-187",
                        0
                    ],
                    "destination": [
                        "obj-39",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-187",
                        0
                    ],
                    "destination": [
                        "obj-13",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-180",
                        7
                    ],
                    "destination": [
                        "obj-188",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-188",
                        0
                    ],
                    "destination": [
                        "obj-108",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-188",
                        0
                    ],
                    "destination": [
                        "obj-63",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-188",
                        0
                    ],
                    "destination": [
                        "obj-39",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-188",
                        0
                    ],
                    "destination": [
                        "obj-13",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-124",
                        0
                    ],
                    "destination": [
                        "obj-189",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-189",
                        0
                    ],
                    "destination": [
                        "obj-13",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-124",
                        1
                    ],
                    "destination": [
                        "obj-189",
                        1
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-189",
                        1
                    ],
                    "destination": [
                        "obj-39",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-124",
                        2
                    ],
                    "destination": [
                        "obj-189",
                        2
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-189",
                        2
                    ],
                    "destination": [
                        "obj-63",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-124",
                        3
                    ],
                    "destination": [
                        "obj-189",
                        3
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-189",
                        3
                    ],
                    "destination": [
                        "obj-108",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-191",
                        0
                    ],
                    "destination": [
                        "obj-190",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-190",
                        0
                    ],
                    "destination": [
                        "obj-192",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-192",
                        0
                    ],
                    "destination": [
                        "obj-189",
                        4
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-193",
                        0
                    ],
                    "destination": [
                        "obj-189",
                        5
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-189",
                        0
                    ],
                    "destination": [
                        "obj-194",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-194",
                        0
                    ],
                    "destination": [
                        "obj-195",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-195",
                        0
                    ],
                    "destination": [
                        "obj-196",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-189",
                        1
                    ],
                    "destination": [
                        "obj-197",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-197",
                        0
                    ],
                    "destination": [
                        "obj-198",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-198",
                        0
                    ],
                    "destination": [
                        "obj-199",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-189",
                        2
                    ],
                    "destination": [
                        "obj-200",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-200",
                        0
                    ],
                    "destination": [
                        "obj-201",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-201",
                        0
                    ],
                    "destination": [
                        "obj-202",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-189",
                        3
                    ],
                    "destination": [
                        "obj-203",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-203",
                        0
                    ],
                    "destination": [
                        "obj-204",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-204",
                        0
                    ],
                    "destination": [
                        "obj-205",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-189",
                        0
                    ],
                    "destination": [
                        "obj-207",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-207",
                        0
                    ],
                    "destination": [
                        "obj-208",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-208",
                        0
                    ],
                    "destination": [
                        "obj-209",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-209",
                        0
                    ],
                    "destination": [
                        "obj-206",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-189",
                        1
                    ],
                    "destination": [
                        "obj-210",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-210",
                        0
                    ],
                    "destination": [
                        "obj-211",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-211",
                        0
                    ],
                    "destination": [
                        "obj-212",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-212",
                        0
                    ],
                    "destination": [
                        "obj-206",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-189",
                        2
                    ],
                    "destination": [
                        "obj-213",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-213",
                        0
                    ],
                    "destination": [
                        "obj-214",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-214",
                        0
                    ],
                    "destination": [
                        "obj-215",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-215",
                        0
                    ],
                    "destination": [
                        "obj-206",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-189",
                        3
                    ],
                    "destination": [
                        "obj-216",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-216",
                        0
                    ],
                    "destination": [
                        "obj-217",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-217",
                        0
                    ],
                    "destination": [
                        "obj-218",
                        0
                    ]
                }
            },
            {
                "patchline": {
                    "source": [
                        "obj-218",
                        0
                    ],
                    "destination": [
                        "obj-206",
                        0
                    ]
                }
            }
        ],
        "originid": "pat-909",
        "dependency_cache": [
            {
                "name": "qmw_density_field_to_resonator_local.js",
                "bootpath": "/Users/zlayton/QuantumSonification/max",
                "patcherrelativepath": ".",
                "type": "TEXT",
                "implicit": 1
            },
            {
                "name": "qmw_four_qubit_event_engine_v1.js",
                "bootpath": "/Users/zlayton/QuantumSonification/max",
                "patcherrelativepath": ".",
                "type": "TEXT",
                "implicit": 1
            }
        ]
    }
}
